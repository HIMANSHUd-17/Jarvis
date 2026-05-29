#!/bin/bash
# JARVIS Frontend Server Launcher (macOS/Linux)

PORT=8000
WEB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔═══════════════════════════════════════════╗"
echo "║       JARVIS Web Dashboard Server         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "📡 Starting server on port $PORT"
echo "📁 Serving from: $WEB_DIR"
echo ""
echo "🔗 Open in browser:"
echo "   http://localhost:$PORT"
echo ""
echo "⚠️  Make sure backend is running:"
echo "   cd backend && python server.py"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$WEB_DIR"
python3 -m http.server $PORT
