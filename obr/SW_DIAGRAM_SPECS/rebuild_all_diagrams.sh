#!/bin/bash
# Skript na hromadnú rekompiláciu všetkých Mermaid diagramov v SW_DIAGRAM_SPECS
# Vygeneruje PNG, SVG a PDF pre každý *.mmd súbor

set -e

cd "$(dirname "$0")"

for mmd in */*.mmd; do
  base="${mmd%.mmd}"
  echo "Kompilujem $mmd ..."
  npx -y @mermaid-js/mermaid-cli -i "$mmd" -o "${base}.png" -w 5000 -s 3
  npx -y @mermaid-js/mermaid-cli -i "$mmd" -o "${base}.svg"
  npx -y @mermaid-js/mermaid-cli -i "$mmd" -o "${base}.pdf"
  echo "Hotovo: $base.[png|svg|pdf]"
done

echo "Všetky diagramy boli úspešne vygenerované."
