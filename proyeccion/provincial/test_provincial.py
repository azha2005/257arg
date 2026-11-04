"""Pruebas del adaptador provincial: python -X utf8 proyeccion/provincial/test_provincial.py
Arma una «eleccion provincial» falsa con diputados nacionales 2025 de la PBA (nombres de partido en vez de codigos,
sin padron, con una lista sin bloque), la ingresa con ingestar.py y la proyecta contra si misma."""
import os, sys, tempfile, unittest
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..")]
import config as cf
import ingestar
import proyectar_prov as pp

PROY = os.path.join(HERE, "..")


class Provincial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m = pd.read_pickle(os.path.join(PROY, "mesas_2025bl.pkl"))
        cls.m = m[m.distrito_id == "02"]
        nom = ingestar.ambitos("02").set_index("seccion_id").nombre
        L = cls.m.melt(id_vars=["seccion_id", "circuito", "mesa_id"], value_vars=["LLA", "FP", "PU", "FIT", "OTRAS", "BLANCO", "NULO"],
                       var_name="lista", value_name="votos")
        L["lista"] = L.lista.replace({"BLANCO": "VOTOS EN BLANCO", "NULO": "VOTOS NULOS", "OTRAS": "LISTA SIN BLOQUE"})
        L["partido"] = L.seccion_id.map(nom).str.title()
        L["circuito"] = L.circuito.str.zfill(5)               # con ceros a la izquierda, como suelen venir
        cls.dir = tempfile.mkdtemp()
        L.drop(columns="seccion_id").rename(columns={"mesa_id": "mesa"}).to_csv(os.path.join(cls.dir, "mesas.csv"), index=False)
        pd.DataFrame({"lista": ["LLA", "FP", "PU", "FIT"], "bloque": ["LLA", "FP", "PU", "FIT"]}).to_csv(
            os.path.join(cls.dir, "listas.csv"), index=False)
        cf.ELECCIONES["prueba_prov"] = dict(provincia="pba", archivo=os.path.join(cls.dir, "mesas.csv"),
                                            columnas={"partido": "seccion"}, cargo=None,
                                            listas=os.path.join(cls.dir, "listas.csv"))
        ingestar.main("prueba_prov")
        cls.w = pd.read_pickle(os.path.join(PROY, "mesas_prueba_prov.pkl"))

    @classmethod
    def tearDownClass(cls):
        for f in ("mesas_prueba_prov.pkl", "circ_prueba_prov.pkl"):
            os.remove(os.path.join(PROY, f))

    def test_ingesta_conserva_votos_y_padron(self):
        for b in ("LLA", "FP", "PU", "FIT", "BLANCO", "NULO"):
            self.assertEqual(self.w[b].sum(), self.m[b].sum())
        self.assertEqual(self.w.OTRAS.sum(), self.m.OTRAS.sum())          # lista sin bloque -> OTRAS
        self.assertEqual(len(self.w), len(self.m))
        self.assertEqual(self.w.e.sum(), self.m.e.sum())                  # padron tomado de la nacional

    def test_destino_igual_al_origen_queda_cerca(self):
        a = ingestar_a_actas(self.w.sample(400, random_state=3))
        R = pp.calcular(a, "pba", "prueba_prov", ["LLA", "FP", "PU", "FIT", "OTRAS"], nboot=20)
        t = self.w[R["blocs"]].sum()
        # destino = origen: no hay cambio que estimar; solo queda el ruido de mesa dentro del circuito
        np.testing.assert_allclose(R["pt"], 100 * t / t.sum(), atol=1.0)
        self.assertEqual(sorted(R["distritos"]), ["%02d" % i for i in range(1, 9)])

    def test_bancas_suman_lo_que_se_elige(self):
        a = ingestar_a_actas(self.w.sample(300, random_state=4))
        R = pp.calcular(a, "pba", "2023p", ["LLA", "FP", "PU", "FIT", "OTRAS"], nboot=20)
        B = pp.bancas(R, "pba", 2027)
        for (cam, s), (pt, lo, hi) in B.items():
            self.assertEqual(pt.sum(), cf.PROVINCIAS["pba"]["camaras"][cam][s])
            self.assertEqual(pt[R["blocs"].index("OTRAS")], 0)
            v = R["distrito_pt"][list(R["distritos"]).index("%02d" % s)]
            self.assertTrue((pt[v < v.sum() / pt.sum()] == 0).all())     # sin cociente, sin bancas

    def test_hare_piso(self):
        np.testing.assert_array_equal(pp.hare_piso([50, 30, 15, 5], 8), [4, 3, 1, 0])      # 5 % < cociente 12,5 %
        np.testing.assert_array_equal(pp.hare_piso([46, 44, 10], 3, np.array([1, 1, 0], bool)), [2, 1, 0])
        # dos listas con cociente y tres bancas de resto: los restos no van a las que no lo alcanzaron
        np.testing.assert_array_equal(pp.hare_piso([42.6, 41.2, 1.7, 4.8, 9.7], 15, np.array([1, 1, 1, 1, 0], bool)),
                                      [8, 7, 0, 0, 0])
        for n in (3, 5, 9, 18):
            v = np.random.default_rng(n).dirichlet(np.ones(6)) * 1e5
            self.assertEqual(pp.hare_piso(v, n).sum(), n)
        # art. 110: ninguna llega al cociente -> el piso baja a la mitad; mas listas que bancas -> las mas votadas
        np.testing.assert_array_equal(pp.hare_piso([30, 28, 22, 20], 2), [1, 1, 0, 0])
        np.testing.assert_array_equal(pp.hare_piso([30, 28, 22, 20], 3), [1, 1, 1, 0])

    def test_bancas_2023_como_la_wikipedia(self):
        """Provinciales 2023 por partido (catalogo de la provincia) -> las 69 bancas de la Wikipedia, seccion por seccion."""
        f = cf.ELECCIONES["pba2023"]["archivo"]
        if not os.path.exists(f):
            self.skipTest("falta " + f)
        d = pd.read_csv(f, dtype=str, encoding="latin-1")
        d = d[(d.eleccion == "2023") & d.cargo.str.contains("SENADORES PROV|DIPUTADOS PROV", case=False)]
        d["votos"] = pd.to_numeric(d.votos)
        wiki = {1: (7, 4, 4), 2: (2, 2, 1), 3: (5, 2, 2), 4: (5, 5, 4), 5: (4, 4, 3), 6: (2, 2, 2), 7: (2, 2, 2), 8: (2, 1, 0)}
        for (sid, cargo), g in d.groupby(["seccion_id", "cargo"]):
            s, cam = int(sid), "senadores" if "SEN" in cargo.upper() else "diputados"
            self.assertIn(s, cf.PROVINCIAS["pba"]["renueva"][2027][cam])
            t = g[~g.lista.str.contains("BLANCO|NULO")].groupby("lista").votos.sum()
            b = dict(zip(t.index, pp.hare_piso(t.values, cf.PROVINCIAS["pba"]["camaras"][cam][s])))
            self.assertEqual((b["UNION POR LA PATRIA"], b["JUNTOS POR EL CAMBIO"], b["LA LIBERTAD AVANZA"]), wiki[s], s)


def ingestar_a_actas(w):
    import ensayo
    return ensayo.actas(w, ["LLA", "FP", "PU", "FIT", "OTRAS"])


if __name__ == "__main__":
    unittest.main()
