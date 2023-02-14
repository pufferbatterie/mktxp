from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.hotspot_ds import HotspotMetricsDataSource


class HotspotCollector(BaseCollector):
    ''' Hotspot Metrics collector
    '''

    @staticmethod
    def collect(router_entry):
        print('collecting hotspot')
        if not router_entry.config_entry.dhcp:
            return

        hotspot_hosts_records = HotspotMetricsDataSource.metric_records(router_entry)

        if hotspot_hosts_records:
            # calculate per hotspot server server
            count_host_by_server = {}
            count_hostactive_by_server = {}
            for r in hotspot_hosts_records:
                if r.get('server'):
                    count_host_by_server[r['server']] = count_host_by_server.get(r['server'], 0) + 1
                    if r.get('authorized', 'false') == 'true':
                        count_hostactive_by_server[r['server']] = count_hostactive_by_server.get(r['server'], 0) + 1

            hotspot_hosts_servers_records = [
                {
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'server': key, 'count': value
                } for key, value in count_host_by_server.items()]

            if hotspot_hosts_servers_records:
                yield BaseCollector.gauge_collector('hotspot_hosts_count',
                                                    'Number of hosts per hotspot server',
                                                    hotspot_hosts_servers_records, 'count',
                                                    ['server'])

            hotspot_hostsactive_servers_records = [
                {
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'server': key, 'count': value
                } for key, value in count_hostactive_by_server.items()]

            if hotspot_hostsactive_servers_records:
                yield BaseCollector.gauge_collector('hotspot_hosts_active_count',
                                                    'Number of hosts active per hotspot server',
                                                    hotspot_hostsactive_servers_records, 'count',
                                                    ['server'])
