# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import ipaddress
from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.pool_ds import PoolMetricsDataSource, PoolUsedMetricsDataSource


class PoolCollector(BaseCollector):
    ''' IP Pool Metrics collector
    '''

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.pool:
            return

        # initialize all pool counts, including those currently not used
        pool_records = PoolMetricsDataSource.metric_records(router_entry, metric_labels=['name', 'ranges'])
        if pool_records:
            pool_used_labels = ['pool']
            pool_used_counts = {pool_record['name']: 0 for pool_record in pool_records}

            pool_ranges = {r['name']: r.get('ranges') for r in pool_records}

            # compile pool_size_records
            pool_size_records = []
            for pool_name, range in pool_ranges.items():
                pool_size = int(ipaddress.IPv4Address(range.split('-')[1])) \
                            - int(ipaddress.IPv4Address(range.split('-')[0])) \
                            + 1
                pool_size_records.append({
                    MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                    MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                    'pool': pool_name, 'count': pool_size
                })

            # for pools in usage, calculate the current numbers
            pool_used_records = PoolUsedMetricsDataSource.metric_records(router_entry, metric_labels=pool_used_labels)
            for pool_used_record in pool_used_records:
                pool_used_counts[pool_used_record['pool']] = pool_used_counts.get(pool_used_record['pool'], 0) + 1

            # compile used-per-pool records
            used_per_pool_records = [
                {MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                 MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                 'pool': key, 'count': value} for key, value in pool_used_counts.items()]

            # yield used-per-pool metrics
            used_per_pool_metrics = BaseCollector.gauge_collector('ip_pool_used',
                                                                  'Number of used addresses per IP pool',
                                                                  used_per_pool_records, 'count', ['pool'])
            yield used_per_pool_metrics

            yield BaseCollector.gauge_collector('ip_pool_size',
                                                'Number of addresses per IP pool',
                                                pool_size_records, 'count', ['pool'])


if __name__ == '__main__':
    import ipaddress
    s = ipaddress.IPv4Address('192.168.0.1')
    e = ipaddress.IPv4Address('192.168.0.255')
    print(int(e) - int(s))
