import { MapContainer, Marker, Polyline, TileLayer, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

function ClickHandler({ onAddLocation }) {
  useMapEvents({
    click(event) {
      const { lat, lng } = event.latlng;
      onAddLocation([Number(lat.toFixed(6)), Number(lng.toFixed(6))]);
    },
  });

  return null;
}

export default function MapView({ locations, route, onAddLocation }) {
  return (
    <MapContainer center={[20.5937, 78.9629]} zoom={5} scrollWheelZoom className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler onAddLocation={onAddLocation} />
      {locations.map((position, index) => (
        <Marker key={`${position[0]}-${position[1]}-${index}`} position={position} />
      ))}
      {route.length > 1 && <Polyline positions={route} color="#f97316" weight={5} />}
    </MapContainer>
  );
}
