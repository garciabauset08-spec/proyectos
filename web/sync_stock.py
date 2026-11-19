#!/usr/bin/env python3
"""
Sincroniza precios, stock e ids de variante con la tienda oficial.

Lee el catálogo público https://danzcollective.com/products.json (no necesita
claves) y actualiza static/data/productos.json. Conserva nuestros textos,
fotos y alt. Si la tienda no responde, deja el archivo como estaba y termina
sin error, para que la web se pueda publicar igual.

Uso:  python3 sync_stock.py
      python3 sync_stock.py --desde catalogo.json   (prueba con un archivo guardado)
"""
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
FILE = ROOT / "static/data/productos.json"
URL = "https://danzcollective.com/products.json?limit=50"
ORDER = ["S", "M", "L", "XL"]


def main():
    data = json.loads(FILE.read_text(encoding="utf-8"))
    if "--desde" in sys.argv:
        src = pathlib.Path(sys.argv[sys.argv.index("--desde") + 1])
        remote = {p["handle"]: p for p in json.loads(src.read_text(encoding="utf-8"))["products"]}
        return merge(data, remote)
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (compatible; danzflor-web-build/1.0)", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            remote = {p["handle"]: p for p in json.load(r)["products"]}
    except Exception as ex:  # sin red: publicamos con el último stock conocido
        print(f"AVISO · No se pudo leer la tienda ({ex}). Se mantiene el stock anterior.")
        return 0
    return merge(data, remote)


def merge(data, remote):
    changes = []
    for p in data["productos"]:
        rp = remote.get(p["handle"])
        if not rp:
            changes.append(f"{p['handle']}: ya no está publicado en la tienda (revísalo)")
            continue
        price = float(rp["variants"][0]["price"])
        if price != p["precio"]:
            changes.append(f"{p['handle']}: precio {p['precio']} → {price}")
            p["precio"] = price
        variants = []
        for v in rp["variants"]:
            size = "Única" if v["title"] == "Default Title" else v["title"]
            variants.append({"id": v["id"], "talla": size, "disponible": bool(v["available"])})
        variants.sort(key=lambda v: ORDER.index(v["talla"]) if v["talla"] in ORDER else 99)
        old = {v["talla"]: v["disponible"] for v in p["variantes"]}
        for v in variants:
            if old.get(v["talla"]) != v["disponible"]:
                changes.append(f"{p['handle']} {v['talla']}: {'disponible' if v['disponible'] else 'agotada'}")
        p["variantes"] = variants

    new = sorted(set(remote) - {p["handle"] for p in data["productos"]})
    for h in new:
        changes.append(f"{h}: producto NUEVO en la tienda. Añádelo a productos.json con sus textos y fotos (ver README).")

    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Stock sincronizado." + ("\n  " + "\n  ".join(changes) if changes else " Sin cambios."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
