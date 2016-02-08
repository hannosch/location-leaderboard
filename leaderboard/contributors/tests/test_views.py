import datetime
import json
import time

from django.core.urlresolvers import reverse
from django.test import TestCase

from leaderboard.fxa.tests.test_client import MockRequestTestMixin
from leaderboard.contributors.models import Contribution
from leaderboard.contributors.tests.test_models import ContributorFactory
from leaderboard.locations.tests.test_models import CountryFactory
from leaderboard.utils.compression import gzip_compress


class SubmitContributionTests(MockRequestTestMixin, TestCase):

    def setUp(self):
        super(SubmitContributionTests, self).setUp()
        fxa_profile_data = self.setup_profile_call()
        self.setup_verify_call(uid=fxa_profile_data['uid'])
        self.country = CountryFactory()
        self.contributor = ContributorFactory(fxa_uid=fxa_profile_data['uid'])

    def test_submit_multiple_observations(self):
        today = datetime.date.today()
        now = time.mktime(today.timetuple())
        one_day = 24 * 60 * 60

        observation_data = {
            'items': [
                # A contribution for tile1 at time1
                {
                    'time': now,
                    'tile_easting_m': -8872100,
                    'tile_northing_m': 5435700,
                    'observations': 100,
                },
                # A contribution for tile1 at time 1
                {
                    'time': now,
                    'tile_easting_m': -8872100,
                    'tile_northing_m': 5435700,
                    'observations': 100,
                },
                # A contribution for tile2 at time1
                {
                    'time': now,
                    'tile_easting_m': -8892100,
                    'tile_northing_m': 5435700,
                    'observations': 100,
                },
                # A contribution for tile2 at time2
                {
                    'time': now + one_day,
                    'tile_easting_m': -8892100,
                    'tile_northing_m': 5435700,
                    'observations': 100,
                },
            ],
        }

        payload = json.dumps(observation_data)

        response = self.client.post(
            reverse('contributions-create'),
            payload,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer asdf',
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Contribution.objects.count(), 4)

        self.assertEqual(Contribution.objects.filter(date=today).count(), 3)
        for contribution in Contribution.objects.filter(date=today):
            self.assertEqual(contribution.contributor, self.contributor)
            self.assertEqual(contribution.country, self.country)
            self.assertEqual(contribution.observations, 100)

        contribution = Contribution.objects.get(
            date=(today + datetime.timedelta(days=1)))
        self.assertEqual(contribution.contributor, self.contributor)
        self.assertEqual(contribution.country, self.country)
        self.assertEqual(contribution.observations, 100)

    def test_missing_authentication_token_returns_401(self):
        response = self.client.post(
            reverse('contributions-create'),
            '',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)

    def test_invalid_data_returns_400(self):
        observation_data = {
            'items': [
                {
                    'time': 'asdf',
                    'tile_easting_m': 'asdf',
                    'tile_northing_m': 'asdf',
                    'observations': 'asdf',
                },
            ],
        }

        payload = json.dumps(observation_data)

        response = self.client.post(
            reverse('contributions-create'),
            payload,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer asdf',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Contribution.objects.all().count(), 0)
        errors = response.data[0]
        self.assertIn('time', errors)
        self.assertIn('tile_easting_m', errors)
        self.assertIn('tile_northing_m', errors)
        self.assertIn('observations', errors)

    def test_submit_observations_with_gzipped_data(self):
        observation_data = {
            'items': [
                {
                    'time': time.time(),
                    'tile_easting_m': -8872100,
                    'tile_northing_m': 5435700,
                    'observations': 100,
                },
            ],
        }

        payload = gzip_compress(json.dumps(observation_data))

        response = self.client.post(
            reverse('contributions-create'),
            payload,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer asdf',
            HTTP_CONTENT_ENCODING='gzip',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contribution.objects.all().count(), 1)

    def test_invalid_gzip_data_raises_400(self):
        response = self.client.post(
            reverse('contributions-create'),
            'asdf',
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer asdf',
            HTTP_CONTENT_ENCODING='gzip',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('gzip error', response.content)
