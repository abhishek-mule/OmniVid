'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { simpleApi } from '@/lib/api';

export default function WsTestPage() {
  const params = useSearchParams();
  const id = params.get('id');
  const [messages, setMessages] = useState<string[]>([]);
  const [status, setStatus] = useState<string>('idle');

  useEffect(() => {
    if (!id) return;
    const url = simpleApi.getWebSocketUrl(id);
    setStatus('connecting');
    const ws = new WebSocket(url);
    ws.onopen = () => setStatus('open');
    ws.onmessage = (ev) => setMessages((prev) => [...prev, ev.data]);
    ws.onerror = () => setStatus('error');
    ws.onclose = () => setStatus('closed');
    return () => { try { ws.close(); } catch {} };
  }, [id]);

  return (
    <div className="p-4">
      <h1 className="text-lg font-semibold">WebSocket Test</h1>
      <p className="text-sm text-gray-600">videoId: {id ?? '(missing)'}</p>
      <p className="text-sm">Status: <span className="font-mono">{status}</span></p>
      <div className="mt-3 border rounded p-2 h-64 overflow-auto text-xs bg-gray-50">
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages yet.</p>
        ) : (
          messages.map((m, i) => <pre key={i}>{m}</pre>)
        )}
      </div>
      <p className="mt-2 text-xs text-gray-500">Append `?id=&lt;videoId&gt;` to the URL to connect.</p>
    </div>
  );
}