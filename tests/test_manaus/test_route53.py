from unittest.mock import MagicMock

from senza.manaus.route53 import Route53HostedZone, Route53Record, Route53


# TODO test hosted zone

def test_hosted_zone_from_boto_dict():
    hosted_zone_dict = {'Config': {'PrivateZone': False},
                        'CallerReference': '0000',
                        'ResourceRecordSetCount': 42,
                        'Id': '/hostedzone/random1',
                        'Name': 'example.com.'}
    hosted_zone = Route53HostedZone.from_boto_dict(hosted_zone_dict)

    assert hosted_zone.id == "/hostedzone/random1"
    assert hosted_zone.name == 'example.com.'
    assert hosted_zone.caller_reference == '0000'
    assert hosted_zone.resource_record_set_count == 42
    assert hosted_zone.config == {'PrivateZone': False}


def test_record_from_boto_dict():
    record_dict = {'Name': 'domain.example.com.',
                   'ResourceRecords': [{'Value': '127.0.0.1'}],
                   'TTL': 600,
                   'Type': 'A'}
    record = Route53Record.from_boto_dict(record_dict)
    assert record.name == 'domain.example.com.'
    assert record.ttl == 600
    assert record.region is None


def test_route53_hosted_zones(monkeypatch):
    m_client = MagicMock()
    m_client.return_value = m_client
    hosted_zone1 = {'Config': {'PrivateZone': False},
                    'CallerReference': '0000',
                    'ResourceRecordSetCount': 42,
                    'Id': '/hostedzone/random1',
                    'Name': 'example.com.'}
    hosted_zone2 = {'Config': {'PrivateZone': False},
                    'CallerReference': '0000',
                    'ResourceRecordSetCount': 7,
                    'Id': '/hostedzone/random2',
                    'Name': 'example.net.'}
    m_client.list_hosted_zones.return_value = {'MaxItems': '100',
                                               'ResponseMetadata': {
                                                   'HTTPStatusCode': 200,
                                                   'RequestId': 'FakeId'},
                                               'HostedZones': [hosted_zone1,
                                                               hosted_zone2],
                                               'IsTruncated': False}
    monkeypatch.setattr('boto3.client', m_client)

    route53 = Route53()
    hosted_zones = list(route53.get_hosted_zones())
    assert len(hosted_zones) == 2
    assert hosted_zones[0].id == '/hostedzone/random1'
    assert hosted_zones[1].name == 'example.net.'


def test_get_records(monkeypatch):
    m_client = MagicMock()
    m_client.return_value = m_client
    hosted_zone1 = {'Config': {'PrivateZone': False},
                    'CallerReference': '0000',
                    'ResourceRecordSetCount': 42,
                    'Id': '/hostedzone/random1',
                    'Name': 'example.com.'}
    mock_records = [{'Name': 'domain.example.com.',
                     'ResourceRecords': [{'Value': '127.0.0.1'}],
                     'TTL': 600,
                     'Type': 'A'},
                    {'Name': 'domain.example.net.',
                     'ResourceRecords': [{'Value': '127.0.0.1'}],
                     'TTL': 600,
                     'Type': 'A'}
                    ]
    m_client.list_hosted_zones.return_value = {'MaxItems': '100',
                                               'ResponseMetadata': {
                                                   'HTTPStatusCode': 200,
                                                   'RequestId': 'FakeId'},
                                               'HostedZones': [hosted_zone1],
                                               'IsTruncated': False}
    m_client.list_resource_record_sets.return_value = {
        "ResourceRecordSets": mock_records}
    monkeypatch.setattr('boto3.client', m_client)

    route53 = Route53()
    records = list(route53.get_records())
    assert len(records) == 2

    records = list(route53.get_records(name='domain.example.net.'))
    assert len(records) == 1
    assert records[0].name == 'domain.example.net.'
