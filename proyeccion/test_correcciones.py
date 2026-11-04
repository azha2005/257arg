"""Regresiones de fallos metodologicos encontrados en la revision del 28-oct-2026."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import fotos_modelo as fm
import proyectar_fotos as pf
import congreso as cg
from enlace import alinear

HERE=Path(__file__).resolve().parent


class Correcciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=pf.leer(HERE/'fotos25/actas.csv')
        cls.r=pf.calcular(cls.a,'2023p,2021bl',nboot=40,seed=17)

    def test_foto_duplicada_no_cambia_voto(self):
        copy=self.a[self.a.mesa_key==self.a.mesa_key.iloc[0]].copy()
        copy['foto']='otra_imagen.jpg'
        r=pf.calcular(pd.concat([self.a,copy]),'2023p,2021bl',nboot=40,seed=17)
        self.assertEqual(len(r['F']),len(self.r['F']))
        np.testing.assert_allclose(r['pt'],self.r['pt'],atol=1e-10)
        np.testing.assert_allclose(r['bs'],self.r['bs'],atol=1e-10)

    def test_conflicto_no_se_suma(self):
        copy=self.a[self.a.mesa_key==self.a.mesa_key.iloc[0]].copy()
        copy['foto']='otra_imagen.jpg'
        copy.loc[copy.index[0],'votos']+=1
        with self.assertRaises(ValueError):
            pf.normalizar_actas(pd.concat([self.a,copy]))

    def test_pesos_por_fuerza(self):
        for s in self.r['soporte']:
            self.assertAlmostEqual(s['peso_amba'],self.r['share']['AMBA'])

    def test_fuerza_ausente_no_es_cero(self):
        a=self.a[self.a.bloque!='PU'].copy();a['completa']='no'
        r=pf.calcular(a,'2023p,2021bl',nboot=40)
        self.assertIn('PU',r['blocs'])
        self.assertFalse(r['inferencia_valida'])
        self.assertTrue(np.isnan(r['prob_primero']).all())

    def test_bootstrap_sin_fuerza_no_publica_probabilidad(self):
        row=self.a[self.a.bloque=='PU'].iloc[0]
        same=(self.a.distrito_id==row.distrito_id)&(self.a.seccion_id==row.seccion_id)&(self.a.circuito==row.circuito)
        a=self.a[same|(self.a.bloque!='PU')].copy();a['completa']='no'
        r=pf.calcular(a,'2023p,2021bl',nboot=80)
        self.assertTrue(np.isfinite(r['pt']).all())
        self.assertFalse(r['inferencia_valida'])
        self.assertTrue(np.isnan(r['prob_primero']).all())

    def test_primero_se_compara_con_todos(self):
        p=fm.probabilidades_primero(np.array([[40,30,30],[35,25,40],[36,34,30]]))
        np.testing.assert_allclose(p,[2/3,0,1/3])
        self.assertTrue(np.isnan(fm.probabilidades_primero(np.array([[np.nan,1,2]]))).all())

    def test_parcial_no_reduce_prior_de_fuerza_ausente(self):
        d=pd.DataFrame({'LLA':[4000.],'FP':[3500.],'PU':[1500.],'OTRAS':[1000.]},index=['04'])
        a=pd.DataFrame({'distrito_id':['04','04'],'bloque':['LLA','FP'],'lista':['LLA','FP'],
                        'votos':[1000.,1000.],'completa':['no','no']})
        pd.testing.assert_frame_equal(cg.provinciales(d,2025)[0],cg.provinciales(d,2025,a)[0])

    def test_enlace_no_pierde_unidades(self):
        src=pd.DataFrame({'distrito_id':['01','01'],'seccion_id':[1,2],'circuito':['1','2'],'a':[.1,.9]})
        dst=pd.DataFrame({'distrito_id':['01','01','99'],'seccion_id':[1,3,1],'circuito':['1','9','1']})
        x,n=alinear(dst,src,['a'],np.array([3.,1.]),[('circuito',['distrito_id','seccion_id','circuito']),('distrito',['distrito_id'])])
        np.testing.assert_allclose(x[:,0],[.1,.3,.3])
        self.assertEqual(n.tolist(),['circuito','distrito','nacional'])

    def test_congreso_y_nacional_comparten_simulaciones(self):
        r=pf.calcular(self.a,'2023p,2021bl',nboot=12,seed=18)
        c=cg.distribucion(r,2025,nboot=12)
        t=c['Dpt'].sum();t['OTRAS']+=t[[x for x in t.index if x.startswith('PROV:')]].sum()
        t=t[r['blocs']];t=100*t/t.sum()
        np.testing.assert_allclose(t,r['pt'])
        self.assertEqual(sum(c['tot'].values()),127)
        self.assertTrue((c['S'].sum(axis=1)==127).all())
        self.assertEqual(c['Dpt'].loc['05','FIT'],0.)
        for d in ['14','15','16','17']:
            self.assertEqual(c['Dpt'].loc[d,'PU'],0.)
        np.testing.assert_allclose(r['bs'].sum(1),100)

    def test_ajuste_rapido_equivale_a_recalcular_actas(self):
        from congreso_motor import preparar
        from fotos_motor import remuestrear_actas
        r=self.r
        fast,pad=preparar(r,2025,cg)
        scale=np.array([pad[d]/r['pad'][d] for d in r['distritos']])[:,None]
        for j in range(4):
            raw=r['distrito_bs'][j];idx=r['indices_boot'][j]
            slow=cg.provinciales(pd.DataFrame(raw*scale,index=r['distritos'],columns=r['blocs']),2025,
                                remuestrear_actas(r,idx),np.random.default_rng(j))[0]
            slow=cg.ceros_estructurales(slow,2025)
            np.testing.assert_allclose(fast(raw,idx,np.random.default_rng(j)),slow,atol=1e-8)

    def test_backtest_conserva_todos_los_votos_y_lo_ya_contado(self):
        import backtest as bt
        old=bt.Y0,bt.Y1,bt.CIRC
        try:
            bt.Y0,bt.Y1,bt.CIRC='2019p','2023p',True
            st,info,_=bt.state()
            self.assertEqual(st['ndist'],24)
            self.assertEqual(info['votos_destino'],info['votos_evaluados'])
            cnt=np.zeros(len(st['e']),bool);cnt[::100]=True
            weights=np.random.default_rng(75).poisson(1,len(cnt))
            V=bt.project_BC(st,cnt,True,'F_tam',bench=False,fitweights=weights)
            np.testing.assert_allclose(V[cnt],st['Vd'][cnt])
            self.assertGreaterEqual(V.min(),0)
            np.testing.assert_allclose(V.sum(1),st['e'],atol=1e-8)
        finally:
            bt.Y0,bt.Y1,bt.CIRC=old


if __name__=='__main__':
    unittest.main()
