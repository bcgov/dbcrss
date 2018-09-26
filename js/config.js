checkup.config = {
	"timeframe": 1 * time.Day,
	"refresh_interval": 60,
	"storage": {
		"url": "https://dbcrss-data.pathfinder.gov.bc.ca"
	},
	"status_text": {
		"healthy": "Service Normal",
		"degraded": "Degraded Service",
		"down": "Service Disruption"
	}
};
