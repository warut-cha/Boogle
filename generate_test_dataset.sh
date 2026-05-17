#!/bin/bash
# Generate multiple test incidents for BOB system testing
# Usage: ./generate_test_dataset.sh [count]

COUNT=${1:-10}
OUTPUT_DIR="test_incidents"

echo "🔧 Generating $COUNT test incidents..."
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Clean old incidents
rm -f "$OUTPUT_DIR"/mock_incident_*.json

# Generate incidents
for i in $(seq 1 $COUNT); do
    echo "[$i/$COUNT] Generating incident..."
    python3 mock_dataset_generator.py > /dev/null 2>&1
    
    # Move generated file to output directory
    LATEST=$(ls -t mock_incident_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        mv "$LATEST" "$OUTPUT_DIR/"
    fi
done

echo ""
echo "✅ Generated $COUNT incidents in $OUTPUT_DIR/"
echo ""
echo "📊 Summary:"
ls -lh "$OUTPUT_DIR"/mock_incident_*.json | wc -l | xargs echo "   Total files:"

echo ""
echo "🔍 Incident types generated:"
for file in "$OUTPUT_DIR"/mock_incident_*.json; do
    python3 -c "import json; data=json.load(open('$file')); print(f\"   - {data['severity']:8s} | {data['title']}\")"
done

echo ""
echo "💡 Usage examples:"
echo "   # Analyze all incidents:"
echo "   for f in $OUTPUT_DIR/*.json; do python3 src/main.py --input \$f; done"
echo ""
echo "   # Test API server:"
echo "   for f in $OUTPUT_DIR/*.json; do curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d @\$f; done"
echo ""

# Made with Bob
