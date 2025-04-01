"""Application configuration"""

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///nyc_transit.db'  # Use SQLite for development
SQLALCHEMY_TRACK_MODIFICATIONS = False

# If password protection is needed, add a secret key
SECRET_KEY = 'your-secret-key-here'  # Use environment variables in production



# Data feed URLs
SUBWAY_FEEDS = {
   'ace': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
   'bdfm': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
   'g' :'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
   'jz' : 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
   'nqrw': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
   'l':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
   'num_s':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
   'sir': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
}

LIRR_FEEDS = {
   'lirr': ' https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/lirr%2Fgtfs-lirr'
}

MNR_FEEDS = {
   'mnr':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr'
}

SERVICE_ALERT_FEEDS = {
   'all_alerts':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fall-alerts',
   'subway_alerts':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts',
   'bus_alerts':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fbus-alerts',
   'lirr_alerts':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Flirr-alerts',
   'mnr_alerts': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fmnr-alerts'
}
# Accessibility data feeds
ELEVATOR_ESCALATOR_FEEDS = {
   'current':"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fnyct_ene.json",
   'upcoming':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fnyct_ene_upcoming.json',
   'equipment':'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fnyct_ene_equipments.json'

}

# Cache settings
CACHE_TIMEOUT = {
   # Category defaults
   'subway_default': 30,      # Subway data: 30 seconds
   'lirr_default': 60,        # LIRR data: 1 minute
   'mnr_default': 60,         # Metro-North data: 1 minute
   'alerts_default': 180,     # Service alerts: 3 minutes
   'accessibility_default': 300,  # Accessibility data: 5 minutes

   # Specific overrides
   'lirr_alerts': 300,        # LIRR alerts: 5 minutes
   'mnr_alerts': 300,         # Metro-North alerts: 5 minutes
   'upcoming': 1800,          # Planned elevator/escalator maintenance: 30 minutes
   'equipment': 3600,         # Equipment info: 1 hour

   'stations_default': 86400,    # Station data: 24 hours
   'routes_default': 86400,      # Route data: 24 hours
   'lines_default': 86400,       # Line shape data: 24 hours
   'route_stops_default': 86400, # Route stop data: 24 hours
}