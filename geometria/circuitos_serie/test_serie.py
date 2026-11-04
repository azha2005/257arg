import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import build as b
from shapely.geometry import Polygon,shape

class TemporalSeriesTests(unittest.TestCase):
    def test_nearest_prefers_previous_on_tie(self):
        a=dict(id='a',desde=2021,hasta=2021,documentada=True,calidad='x')
        z=dict(id='z',desde=2025,hasta=2025,documentada=True,calidad='x')
        self.assertIs(b.choose([z,a],2023),a)
        self.assertIs(b.choose([z,a],2024),z)

    def test_inferred_projection_is_not_documented(self):
        legacy=[s for s in b.sources if s['calidad']=='crs_inferido_sin_prj']
        self.assertEqual(len(legacy),8)
        self.assertTrue(all(not s['documentada'] for s in legacy))

    def test_declared_former_code_is_preserved_separately(self):
        self.assertEqual(b.circuit_code('3396( ex3390)'),('03396','03390'))
        self.assertEqual(b.circuit_code('388A'),('0388A',None))
        self.assertEqual(b.circuit_code(None),(None,None))

    def test_quarantined_sources_remain_registered_with_reason(self):
        blocked={s['id']:s for s in b.sources if s.get('excluir_seleccion_automatica')}
        self.assertIn('galeano_2025_01',blocked)
        self.assertIn('galeano_2021_15',blocked)
        self.assertTrue(all(s['alerta'] for s in blocked.values()))

    def test_replace_only_requested_unit_and_fail_on_wrong_count(self):
        src=dict(id='fixture',desde=2023,hasta=2023,documentada=True)
        def feature(section):return dict(type='Feature',geometry={'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,0]]]},properties=dict(sistema_codigos='galeano',codigo_seccion_fuente=section,codigo_circuito='00001',codigo_distrito='02'))
        original=[feature('052'),feature('053')]
        update=dict(id='update',distrito='02',desde=2023,hasta=2023,versiones=['documentada'],id_fuente='fixture',selector=dict(sistemas_codigos=['galeano'],secciones=['052']),esperados_retirados={'documentada':1},evidencia_url='https://example.test/source',nota='Fixture')
        with patch.object(b,'UPDATES',[update]),patch.object(b,'sources',[src]),patch.object(b,'features_for',return_value=[feature('052')]):
            out,log=b.apply_updates(original,'02',2023,'documentada')
            self.assertEqual(len(out),2)
            self.assertIs(out[0],original[1])
            self.assertEqual(out[1]['properties']['actualizacion_id'],'update')
            self.assertEqual(log[0]['retirados'],1)
            update['esperados_retirados']['documentada']=2
            with self.assertRaisesRegex(ValueError,'retiro esperado'):b.apply_updates(original,'02',2023,'documentada')

    def test_polygon_hole_survives_shp_export(self):
        g=Polygon([(0,0),(3,0),(3,3),(0,3)],holes=[[(1,1),(2,1),(2,2),(1,2)]])
        f=dict(type='Feature',geometry=b.mapping(g),properties=dict(codigo_distrito='01',codigo_seccion_fuente='001',codigo_circuito='00001',anio_fuente_desde=2021,anio_fuente_hasta=2021,id_fuente='fixture',uso_temporal='corte_o_periodo_declarado',calidad_geometria='fixture',geometria_valida=True,indice_fuente=0,identificador_utilizable=True))
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);info=b.export(folder,[f],2021,'documentada',[])
            r=b.shapefile.Reader(str(folder/'shp/circuitos_argentina.shp'),encoding='utf-8')
            recovered=shape(r.shape(0).__geo_interface__);r.close()
            self.assertTrue(g.equals(recovered))
            self.assertEqual(info['registros_shp'],1)

    def test_invalid_line_in_collection_does_not_discard_polygon(self):
        polygon={'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,0]]]}
        geometry={'type':'GeometryCollection','geometries':[polygon,{'type':'LineString','coordinates':[[0,0]]}]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'fixture.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=geometry,properties=dict(circuito='00001',coddepto='001',codprov='01'))])),encoding='utf-8')
            src=dict(id='collection_fixture',archivo='fixture.geojson',esquema='galeano',crs=None,distrito='01',alcance='distrito',desde=2021,hasta=2021,temporalidad='fixture',calidad='fixture',nota='fixture')
            with patch.object(b,'SRC',root),patch.object(b,'cache',{}),patch.object(b,'issues',[]):
                feature=b.features_for(src)[0]
                # La línea de un punto se retira y queda anotada: el GeoJSON tiene que poder leerlo GDAL.
                self.assertEqual(feature['geometry'],polygon)
                self.assertEqual(feature['properties']['error_lectura_geometria'][:22],'IllegalArgumentExcepti')
                self.assertIn('1 LineString de un punto',feature['properties']['depuracion_geometria'])
                self.assertEqual(len(b.polygon_parts(feature['geometry'])),1)
                b.shape(feature['geometry'])

if __name__=='__main__':unittest.main()
