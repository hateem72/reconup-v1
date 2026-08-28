import json
import asyncio
import time
from typing import Dict, List, Any, AsyncGenerator

class EventBus:
    """
    In-memory Server-Sent Events (SSE) bus managing real-time pipeline event queues per batch.
    """
    def __init__(self):
        # Maps batch_id -> list of asyncio.Queue instances
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, batch_id: str) -> asyncio.Queue:
        """Subscribes an SSE client to receive real-time event updates for a batch."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        if batch_id not in self._listeners:
            self._listeners[batch_id] = []
        self._listeners[batch_id].append(queue)
        return queue

    def unsubscribe(self, batch_id: str, queue: asyncio.Queue):
        """Unsubscribes an SSE client when connection closes."""
        if batch_id in self._listeners:
            if queue in self._listeners[batch_id]:
                self._listeners[batch_id].remove(queue)
            if not self._listeners[batch_id]:
                del self._listeners[batch_id]

    def publish_event(self, batch_id: str, event_type: str, data: Dict[str, Any]):
        """Publishes an event to all active listener queues for this batch."""
        if not batch_id or batch_id not in self._listeners:
            return

        payload = {
            "event": event_type,
            "data": data,
            "timestamp": time.time()
        }

        # Put event in all listener queues without blocking
        dead_queues = []
        for q in self._listeners[batch_id]:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead_queues.append(q)

        for dq in dead_queues:
            self.unsubscribe(batch_id, dq)

event_bus = EventBus()

def publish_event(batch_id: str, event_type: str, data: Dict[str, Any]):
    """Global helper to publish SSE events."""
    event_bus.publish_event(batch_id, event_type, data)

async def event_stream_generator(batch_id: str) -> AsyncGenerator[str, None]:
    """Async generator yielding Server-Sent Events formatted strings."""
    queue = event_bus.subscribe(batch_id)
    
    # Send initial connection heartbeat
    init_data = json.dumps({"status": "CONNECTED", "batch_id": batch_id, "time": time.time()})
    yield f"event: CONNECTED\ndata: {init_data}\n\n"

    try:
        while True:
            try:
                # Wait for next event or timeout for heartbeat ping
                msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                event_name = msg.get("event", "MESSAGE")
                payload_json = json.dumps(msg.get("data", {}))
                yield f"event: {event_name}\ndata: {payload_json}\n\n"
            except asyncio.TimeoutError:
                # Send periodic heartbeat ping to keep connection alive
                yield f"event: PING\ndata: {json.dumps({'ping': time.time()})}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        event_bus.unsubscribe(batch_id, queue)
