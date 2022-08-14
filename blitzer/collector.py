#!/usr/bin/env python3
# Simple exporter that fetches status metrics from blizter.de.
# Those metrics are exposed via HTTP for Prometheus.
# Install dependencies: pip install pydantic prometheus-client requests
import time
import pydantic
import prometheus_client as pc
import requests as r

EXPORTER_PORT = 49999


class Status(pydantic.BaseModel):
    fixed_speed_cams: int = pydantic.Field(
        alias='fixed_speedcams'
    )
    mobile_speed_cams: int = pydantic.Field(
        alias='mobile_speedcams'
    )
    partly_fixed_speed_cams: int = pydantic.Field(
        alias='partly_fixed_speedcams'
    )
    danger_spots: int = pydantic.Field(
        alias='dangerspots'
    )
    roadworks: int = pydantic.Field(
        alias='roadworks'
    )
    reports_since_0: int = pydantic.Field(
        alias='reports_since_0'
    )
    user_cnt: int = pydantic.Field(
        alias='user'
    )
    last_changed: str = pydantic.Field(
        alias='last_changed'
    )
    notes_it: str = pydantic.Field(
        alias='notes_it'
    )
    notes_editorial: str = pydantic.Field(
        alias='notes_editorial'
    )

    @pydantic.validator(
        'fixed_speed_cams',
        'mobile_speed_cams',
        'partly_fixed_speed_cams',
        'danger_spots',
        'roadworks',
        'reports_since_0',
        'user_cnt',
        pre=True
    )
    def parse_number(cls, v):
        return int(v.replace('.', ''))


class MetricCollector:

    def __init__(self, base_url: str = 'https://status.blitzer.de/') -> None:
        self.base_url = base_url.rstrip('/')
        self.polling_interval_seconds = 30

        # Prometheus metrics to collect
        self.fixed_speed_cams = pc.Gauge('fixed_speed_cams', 'Total number of fixed speed cams')
        self.mobile_speed_cams = pc.Gauge('mobile_speed_cams', 'Total number of mobile speed cams')
        self.partly_fixed_speed_cams = pc.Gauge('partly_fixed_speed_cams', 'Total number of partly mobile speed cams')
        self.danger_spots = pc.Gauge('danger_spots', 'Total number of fixes danger spots')
        self.roadworks = pc.Gauge('roadworks', 'Total number of road works')
        self.reports_since_0 = pc.Gauge('reports_since_0', 'Total number of reports since ever')
        self.user_cnt = pc.Gauge('user_cnt', 'Total number of currently active users')

        self.info = pc.Info('misc', 'Misc information about the state of Blitzerde')

    @property
    def url(self):
        return f'{self.base_url}/modules/get.php'

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        resp = r.get(self.url)
        resp.raise_for_status()
        json = resp.json()
        json = resp.json()
        status = Status.parse_obj(json)

        self.fixed_speed_cams.set(status.fixed_speed_cams)
        self.mobile_speed_cams.set(status.mobile_speed_cams)
        self.partly_fixed_speed_cams.set(status.partly_fixed_speed_cams)
        self.danger_spots.set(status.danger_spots)
        self.roadworks.set(status.roadworks)
        self.reports_since_0.set(status.reports_since_0)
        self.user_cnt.set(status.user_cnt)

        self.misc.info({
            'last_changed': status.last_changed,
            'notes_it': status.notes_it,
            'notes_editorial': status.notes_editorial,
        })


collector = MetricCollector()
pc.start_http_server(EXPORTER_PORT)
collector.run_metrics_loop()
