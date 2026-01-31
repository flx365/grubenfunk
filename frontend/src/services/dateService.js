// Hilfsfunktion: Gibt das Datum zurück
const formatDate = (timeString) => {
  if (!timeString) return "";
  const date = new Date(timeString);
  return date.toLocaleDateString({
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

// Hilfsfunktion: Gibt die Uhrzeit zurück
const formatTime = (timeString) => {
  if (!timeString) return "";
  const date = new Date(timeString);
  return date.toLocaleTimeString([],{
    hour: '2-digit',
    minute: '2-digit'
  });
};

export { formatDate, formatTime};

