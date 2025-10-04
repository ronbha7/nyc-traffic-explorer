from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Crash


class CrashModelTest(TestCase):
    """Test the Crash model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.crash_data = {
            'collision_id': 123456789,
            'crash_date': timezone.now(),
            'crash_time': '14:30',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'borough': 'MANHATTAN',
            'zip_code': '10001',
            'on_street_name': 'BROADWAY',
            'cross_street_name': '42ND ST',
            'off_street_name': '',
            'number_of_persons_injured': 2,
            'number_of_persons_killed': 0,
            'number_of_pedestrians_injured': 1,
            'number_of_pedestrians_killed': 0,
            'number_of_cyclist_injured': 0,
            'number_of_cyclist_killed': 0,
            'number_of_motorist_injured': 1,
            'number_of_motorist_killed': 0,
            'contributing_factor_vehicle_1': 'Driver Inattention/Distraction',
            'contributing_factor_vehicle_2': '',
            'vehicle_type_code1': 'PASSENGER VEHICLE',
            'vehicle_type_code2': 'PASSENGER VEHICLE'
        }
    
    def test_create_crash(self):
        """Test creating a crash record"""
        crash = Crash.objects.create(**self.crash_data)
        self.assertEqual(crash.collision_id, 123456789)
        self.assertEqual(crash.borough, 'MANHATTAN')
        self.assertEqual(crash.number_of_persons_injured, 2)
        self.assertEqual(crash.number_of_persons_killed, 0)
    
    def test_crash_str_representation(self):
        """Test the string representation of Crash model"""
        crash = Crash.objects.create(**self.crash_data)
        expected_str = f"Crash {crash.collision_id} on {crash.crash_date} in {crash.borough}"
        self.assertEqual(str(crash), expected_str)
    
    def test_total_severity_property(self):
        """Test the total_severity property calculation"""
        # Test with injuries only
        crash = Crash.objects.create(**self.crash_data)
        self.assertEqual(crash.total_severity, 2)  # 2 injuries + 0*10 fatalities
        
        # Test with fatalities
        crash.number_of_persons_killed = 1
        crash.save()
        self.assertEqual(crash.total_severity, 12)  # 2 injuries + 1*10 fatalities
    
    def test_unique_collision_id(self):
        """Test that collision_id must be unique"""
        Crash.objects.create(**self.crash_data)
        
        # Try to create another crash with same collision_id
        with self.assertRaises(Exception):
            Crash.objects.create(**self.crash_data)
    
    def test_model_indexes(self):
        """Test that model indexes are properly set"""
        crash = Crash.objects.create(**self.crash_data)
        
        # Test that we can query by indexed fields efficiently
        crashes_by_date = Crash.objects.filter(crash_date__gte=timezone.now() - timedelta(days=1))
        crashes_by_borough = Crash.objects.filter(borough='MANHATTAN')
        crashes_by_location = Crash.objects.filter(latitude__gte=40.0, longitude__gte=-75.0)
        
        self.assertIn(crash, crashes_by_date)
        self.assertIn(crash, crashes_by_borough)
        self.assertIn(crash, crashes_by_location)


class CrashAPITest(APITestCase):
    """Test the Crash API endpoints"""
    
    def setUp(self):
        """Set up test data for API tests"""
        # Create multiple test crashes
        self.crashes = []
        
        # Manhattan crash
        crash1_data = {
            'collision_id': 111111111,
            'crash_date': timezone.now() - timedelta(days=1),
            'crash_time': '10:00',
            'latitude': 40.7589,
            'longitude': -73.9851,
            'borough': 'MANHATTAN',
            'zip_code': '10019',
            'on_street_name': 'BROADWAY',
            'cross_street_name': '42ND ST',
            'number_of_persons_injured': 1,
            'number_of_persons_killed': 0,
            'contributing_factor_vehicle_1': 'Driver Inattention/Distraction',
            'vehicle_type_code1': 'PASSENGER VEHICLE'
        }
        self.crashes.append(Crash.objects.create(**crash1_data))
        
        # Brooklyn crash
        crash2_data = {
            'collision_id': 222222222,
            'crash_date': timezone.now() - timedelta(days=2),
            'crash_time': '15:30',
            'latitude': 40.6782,
            'longitude': -73.9442,
            'borough': 'BROOKLYN',
            'zip_code': '11201',
            'on_street_name': 'FLATBUSH AVE',
            'cross_street_name': 'ATLANTIC AVE',
            'number_of_persons_injured': 0,
            'number_of_persons_killed': 1,
            'contributing_factor_vehicle_1': 'Following Too Closely',
            'vehicle_type_code1': 'PASSENGER VEHICLE'
        }
        self.crashes.append(Crash.objects.create(**crash2_data))
        
        # Queens crash
        crash3_data = {
            'collision_id': 333333333,
            'crash_date': timezone.now() - timedelta(days=3),
            'crash_time': '08:15',
            'latitude': 40.7282,
            'longitude': -73.7949,
            'borough': 'QUEENS',
            'zip_code': '11375',
            'on_street_name': 'QUEENS BLVD',
            'cross_street_name': 'WOODHAVEN BLVD',
            'number_of_persons_injured': 3,
            'number_of_persons_killed': 0,
            'contributing_factor_vehicle_1': 'Unsafe Speed',
            'vehicle_type_code1': 'PASSENGER VEHICLE'
        }
        self.crashes.append(Crash.objects.create(**crash3_data))
    
    def test_list_crashes(self):
        """Test the list crashes endpoint"""
        url = reverse('crash-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Check that each crash has the expected fields
        for crash_data in response.data:
            self.assertIn('collision_id', crash_data)
            self.assertIn('crash_date', crash_data)
            self.assertIn('latitude', crash_data)
            self.assertIn('longitude', crash_data)
            self.assertIn('borough', crash_data)
            self.assertIn('number_of_persons_injured', crash_data)
            self.assertIn('number_of_persons_killed', crash_data)
            self.assertIn('total_severity', crash_data)
    
    def test_retrieve_crash(self):
        """Test retrieving a specific crash"""
        crash = self.crashes[0]
        url = reverse('crash-detail', kwargs={'pk': crash.collision_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['collision_id'], crash.collision_id)
        self.assertEqual(response.data['borough'], crash.borough)
        self.assertIn('crash_time', response.data)
        self.assertIn('zip_code', response.data)
        self.assertIn('on_street_name', response.data)
        self.assertIn('contributing_factor_vehicle_1', response.data)
    
    def test_retrieve_nonexistent_crash(self):
        """Test retrieving a crash that doesn't exist"""
        url = reverse('crash-detail', kwargs={'pk': 999999999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_search_by_location(self):
        """Test the search by location endpoint"""
        # Search near Manhattan crash (Times Square area)
        url = reverse('crash-search-by-location')
        response = self.client.get(url, {
            'lat': 40.7589,
            'lon': -73.9851,
            'radius': 1000
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertGreater(response.data['count'], 0)
        
        # Check that results contain expected fields
        for result in response.data['results']:
            self.assertIn('collision_id', result)
            self.assertIn('crash_date', result)
            self.assertIn('latitude', result)
            self.assertIn('longitude', result)
            self.assertIn('borough', result)
            self.assertIn('total_severity', result)
    
    def test_search_by_location_missing_params(self):
        """Test search by location with missing parameters"""
        url = reverse('crash-search-by-location')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_search_by_location_invalid_params(self):
        """Test search by location with invalid parameters"""
        url = reverse('crash-search-by-location')
        response = self.client.get(url, {
            'lat': 'invalid',
            'lon': 'invalid',
            'radius': 'invalid'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_stats_endpoint(self):
        """Test the stats endpoint"""
        url = reverse('crash-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_crashes', response.data)
        self.assertIn('total_injured', response.data)
        self.assertIn('total_killed', response.data)
        self.assertIn('borough_breakdown', response.data)
        
        # Check totals
        self.assertEqual(response.data['total_crashes'], 3)
        self.assertEqual(response.data['total_injured'], 4)  # 1 + 0 + 3
        self.assertEqual(response.data['total_killed'], 1)   # 0 + 1 + 0
        
        # Check borough breakdown
        borough_stats = response.data['borough_breakdown']
        self.assertEqual(len(borough_stats), 3)
        
        # Find Manhattan stats
        manhattan_stats = next((b for b in borough_stats if b['borough'] == 'MANHATTAN'), None)
        self.assertIsNotNone(manhattan_stats)
        self.assertEqual(manhattan_stats['crash_count'], 1)
        self.assertEqual(manhattan_stats['injured_count'], 1)
        self.assertEqual(manhattan_stats['killed_count'], 0)


class CrashDataImportTest(TestCase):
    """Test data import functionality"""
    
    def test_sample_data_creation(self):
        """Test creating sample crash data for testing"""
        sample_data = [
            {
                'collision_id': 100000001,
                'crash_date': timezone.now() - timedelta(days=1),
                'crash_time': '09:30',
                'latitude': 40.7831,
                'longitude': -73.9712,
                'borough': 'MANHATTAN',
                'zip_code': '10025',
                'on_street_name': 'BROADWAY',
                'cross_street_name': '96TH ST',
                'number_of_persons_injured': 1,
                'number_of_persons_killed': 0,
                'contributing_factor_vehicle_1': 'Driver Inattention/Distraction',
                'vehicle_type_code1': 'PASSENGER VEHICLE'
            },
            {
                'collision_id': 100000002,
                'crash_date': timezone.now() - timedelta(days=2),
                'crash_time': '16:45',
                'latitude': 40.6892,
                'longitude': -73.9442,
                'borough': 'BROOKLYN',
                'zip_code': '11201',
                'on_street_name': 'ATLANTIC AVE',
                'cross_street_name': 'FLATBUSH AVE',
                'number_of_persons_injured': 2,
                'number_of_persons_killed': 0,
                'contributing_factor_vehicle_1': 'Following Too Closely',
                'vehicle_type_code1': 'PASSENGER VEHICLE'
            }
        ]
        
        # Create crashes from sample data
        created_crashes = []
        for data in sample_data:
            crash = Crash.objects.create(**data)
            created_crashes.append(crash)
        
        # Verify data was created correctly
        self.assertEqual(len(created_crashes), 2)
        self.assertEqual(Crash.objects.count(), 2)
        
        # Test querying the data
        manhattan_crashes = Crash.objects.filter(borough='MANHATTAN')
        brooklyn_crashes = Crash.objects.filter(borough='BROOKLYN')
        
        self.assertEqual(manhattan_crashes.count(), 1)
        self.assertEqual(brooklyn_crashes.count(), 1)
        
        # Test severity calculations
        total_severity = sum(crash.total_severity for crash in created_crashes)
        self.assertEqual(total_severity, 3)  # 1 + 2 injuries
