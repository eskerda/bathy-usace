import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.citybik.es/styles/basic-preview/style.json',
  attributionControl: false,
  bounds: [
    [ -73.65499712979204, 40.56837540618983 ],
    [ -73.46337703739896, 40.610995242688006 ]
  ],
})

map.on('click', (ev) => {
    console.log(map.queryRenderedFeatures(ev.point))
})

map.on('load', () => {
  const waterLayer = 'water_intermittent'
  console.log(map.getStyle().layers)
   map.addSource('bathy', {
     type: 'vector',
     tiles: ['http://localhost:3000/bathy/{z}/{x}/{y}'],
   })

  map.addLayer({
    id: 'bathy',
    type: 'line',
    source: 'bathy',
    'source-layer': 'bathy',
    paint: {
      'line-color': '#000',
      'line-width': 0.8,
    }
  }, waterLayer)


  map.addSource('bathy_pol', {
    type: 'vector',
    tiles: ['http://localhost:3000/bathy_pol/{z}/{x}/{y}'],
  })

  map.addLayer({
    id: 'bathy_pol',
    type: 'fill',
    source: 'bathy_pol',
    'source-layer': 'bathy_pol',
    paint: {
      'fill-color': [
        'interpolate', ['linear'], ['/', ['+', ['to-number', ['get', 'depth_min']], ['to-number', ['get', 'depth_max']]], 2],
          -10, '#08306b',
          -5, '#2171b5',
          -2, '#6baed6',
          -1, '#c6dbef'
      ],
      'fill-opacity': 0.5,
    }
  }, waterLayer)
})
