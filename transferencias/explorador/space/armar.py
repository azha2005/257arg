"""Arma la carpeta publicable del explorador (Streamlit Community Cloud o Space de Hugging Face) con solo los datos que lee.
    python transferencias/explorador/space/armar.py                 # arma transferencias/explorador/space/_build/
    python transferencias/explorador/space/armar.py --subir USUARIO/NOMBRE   # además la sube
      (antes, una vez: python -c "from huggingface_hub import login; login()" con un token de escritura)
La carpeta conserva las rutas del repo, así el código corre sin cambios. Va el MASTER ya leído (cache/master.pkl)
en lugar del xlsx, y los pares ya calculados de cache/pares/ para que el Space arranque con algo hecho."""
import os, sys, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "_build")

PATRONES = [
    "transferencias/*.py", "transferencias/*.csv", "transferencias/circ_*.pkl",
    "transferencias/historicos_1989/*.csv", "transferencias/historicos_1989/*.json", "transferencias/historicos_1989/raw_*.pkl",
    "transferencias/fuentes_1914_1916/correspondencias.csv",
    "transferencias/correspondencias_2013_2017/santa_fe_2022.csv",
    "transferencias/explorador/*.py", "transferencias/explorador/index.html", "transferencias/explorador/LEEME.md",
    "transferencias/explorador/cache/master.pkl", "transferencias/explorador/cache/pares/*.json",
    "datos_oficiales/*/x/**/*mbito*.csv",
    "mapas/mapa*/dataset_*.json", "mapas/mapa*/mapeo_listas_*.csv", "mapas/mapa*/build_*.py", "mapas/mapa1983/caba28.pkl",
    "comun/atlas_leg8399.py",
    "resultados_xlsx/indice_elecciones.csv",
    ".streamlit/config.toml",
]


def armar():
    os.makedirs(OUT, exist_ok=True)
    for x in os.listdir(OUT):                     # todo menos .git: _build es también el repo que lee Streamlit
        if x != ".git":
            (shutil.rmtree if os.path.isdir(os.path.join(OUT, x)) else os.remove)(os.path.join(OUT, x))
    n = tam = 0
    for p in PATRONES:
        fs = [f for f in glob.glob(os.path.join(ROOT, p), recursive=True) if "__MACOSX" not in f]
        if not fs:
            print("  (nada para %s)" % p)
        for f in fs:
            rel = os.path.relpath(f, ROOT)
            dst = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(f, dst)
            n += 1; tam += os.path.getsize(f)
    for f in ("Dockerfile", "requirements.txt", "README.md"):
        shutil.copy2(os.path.join(HERE, f), os.path.join(OUT, f))
    print("%d archivos, %.0f MB en %s" % (n, tam / 2**20, OUT))


def subir(repo):
    from huggingface_hub import HfApi
    with open(os.path.join(OUT, ".gitattributes"), "w") as g:     # Hugging Face guarda los binarios en LFS; GitHub no
        g.write("*.pkl filter=lfs diff=lfs merge=lfs -text\n*.json filter=lfs diff=lfs merge=lfs -text\n")
    api = HfApi()
    api.create_repo(repo, repo_type="space", space_sdk="docker", exist_ok=True)
    api.upload_folder(folder_path=OUT, repo_id=repo, repo_type="space", commit_message="Explorador de transferencias",
                      delete_patterns=["*"] if "--limpiar" in sys.argv else None)
    print("Listo: https://huggingface.co/spaces/%s" % repo)


if __name__ == "__main__":
    armar()
    if "--subir" in sys.argv:
        subir(sys.argv[sys.argv.index("--subir") + 1])
