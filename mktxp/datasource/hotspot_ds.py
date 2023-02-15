from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.utils.utils import parse_mkt_uptime


class HotspotMetricsDataSource:
    ''' Hotspot Metrics data provider
    '''

    @staticmethod
    def metric_records(router_entry, *, add_router_id=True, translate=True, ):

        # [{'id': '*2', 'mac-address': 'EA:52:FD:F7:82:13', 'address': '10.5.50.2', 'to-address': '10.5.50.2', 'server': 'hotspot1', 'uptime': '4m', 'idle-time': '0s', 'idle-timeout': '5m', 'host-dead-time': '0s', 'bytes-in': '234756', 'bytes-out': '109743', 'packets-in': '1773', 'packets-out': '1127', 'found-by': 'UDP :49762 -> 10.5.50.1:53', 'DHCP': 'true', 'authorized': 'false', 'bypassed': 'false'}]
        metric_labels = ['mac-address', 'address', 'to-address', 'server', 'uptime', 'idle-time', 'idle-timeout',
                         'host-dead-time', 'bytes-in', 'bytes-out', 'packets-in', 'packets-out', 'found-by', 'DHCP',
                         'authorized', 'bypassed']

        try:
            hotspot_host_records = router_entry.api_connection.router_api().get_resource(
                '/ip/hotspot/host').get()

            # translation rules
            translation_table = {}
            if 'comment' in metric_labels:
                translation_table['comment'] = lambda c: c if c else ''
            if 'host_name' in metric_labels:
                translation_table['host_name'] = lambda c: c if c else ''
            if 'uptime' in metric_labels and translate:
                translation_table['uptime'] = lambda c: parse_mkt_uptime(c) if c else 0
            if 'idle-time' in metric_labels and translate:
                translation_table['idle-time'] = lambda c: parse_mkt_uptime(c) if c else 0
            if 'idle-timeout' in metric_labels and translate:
                translation_table['idle-timeout'] = lambda c: parse_mkt_uptime(c) if c else 0
            if 'host-dead-time' in metric_labels and translate:
                translation_table['host-dead-time'] = lambda c: parse_mkt_uptime(c) if c else 0

            return BaseDSProcessor.trimmed_records(router_entry, router_records=hotspot_host_records,
                                                   metric_labels=metric_labels, add_router_id=add_router_id,
                                                   translation_table=translation_table)

        except Exception as exc:
            print(
                f'Error getting hotspot info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


if __name__ == '__main__':
    from routeros_api import RouterOsApiPool

    connection = RouterOsApiPool(
        host='172.30.10.1',
        username='admin',
        password='admin',
        port=8728,
        plaintext_login=True,
        use_ssl=False,
        ssl_verify=False)

    hosts = connection.get_api().get_resource('/ip/pool').get()

    print(hosts)
