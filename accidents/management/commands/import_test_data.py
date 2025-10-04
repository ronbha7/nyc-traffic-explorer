from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta
from accidents.models import Crash
import random


class Command(BaseCommand):
    help = 'Import test crash data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of test crashes to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing crash data before importing'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing crash data...')
            Crash.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared existing data')
            )
        
        self.stdout.write(f'Creating {count} test crash records...')
        
        # NYC boroughs and their approximate coordinates
        boroughs = [
            ('MANHATTAN', 40.7831, -73.9712),
            ('BROOKLYN', 40.6782, -73.9442),
            ('QUEENS', 40.7282, -73.7949),
            ('BRONX', 40.8448, -73.8648),
            ('STATEN ISLAND', 40.5795, -74.1502),
        ]
        
        # Common contributing factors
        contributing_factors = [
            'Driver Inattention/Distraction',
            'Following Too Closely',
            'Unsafe Speed',
            'Failure to Yield Right-of-Way',
            'Passing or Lane Usage Improper',
            'Backing Unsafely',
            'Passing Too Closely',
            'Turning Improperly',
            'Traffic Control Disregarded',
            'Other Vehicular',
        ]
        
        # Common vehicle types
        vehicle_types = [
            'PASSENGER VEHICLE',
            'SPORT UTILITY / STATION WAGON',
            'TAXI',
            'PICK-UP TRUCK',
            'LIVERY VEHICLE',
            'BICYCLE',
            'MOTORCYCLE',
            'BUS',
            'TRUCK',
            'VAN',
        ]
        
        # Common street names by borough
        street_names = {
            'MANHATTAN': ['BROADWAY', '5TH AVE', 'LEXINGTON AVE', 'MADISON AVE', 'PARK AVE'],
            'BROOKLYN': ['FLATBUSH AVE', 'ATLANTIC AVE', 'BROOKLYN AVE', '4TH AVE', 'OCEAN PKWY'],
            'QUEENS': ['QUEENS BLVD', 'WOODHAVEN BLVD', 'NORTHERN BLVD', 'ASTORIA BLVD', 'ROCKAWAY BLVD'],
            'BRONX': ['FORDHAM RD', 'CONCOURSE', 'WHITE PLAINS RD', 'BROADWAY', '3RD AVE'],
            'STATEN ISLAND': ['HYLAN BLVD', 'RICHMOND AVE', 'VICTORY BLVD', 'ARTHUR KILL RD', 'RICHMOND RD'],
        }
        
        created_count = 0
        base_collision_id = 100000000
        
        for i in range(count):
            # Select random borough
            borough, base_lat, base_lon = random.choice(boroughs)
            
            # Generate random coordinates within borough (rough approximation)
            lat = base_lat + random.uniform(-0.1, 0.1)
            lon = base_lon + random.uniform(-0.1, 0.1)
            
            # Generate random crash date (within last 2 years)
            crash_date = timezone.now() - timedelta(
                days=random.randint(0, 730),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Generate crash time
            crash_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
            
            # Random injury/fatality counts
            persons_injured = random.randint(0, 5)
            persons_killed = random.randint(0, 2) if random.random() < 0.1 else 0  # 10% chance of fatalities
            
            # Generate pedestrian/cyclist/motorist counts (should sum to total)
            if persons_injured + persons_killed > 0:
                pedestrians_injured = random.randint(0, min(2, persons_injured))
                pedestrians_killed = random.randint(0, min(1, persons_killed))
                remaining_injured = persons_injured - pedestrians_injured
                remaining_killed = persons_killed - pedestrians_killed
                
                cyclist_injured = random.randint(0, min(1, remaining_injured))
                cyclist_killed = random.randint(0, min(1, remaining_killed))
                remaining_injured -= cyclist_injured
                remaining_killed -= cyclist_killed
                
                motorist_injured = remaining_injured
                motorist_killed = remaining_killed
            else:
                pedestrians_injured = pedestrians_killed = 0
                cyclist_injured = cyclist_killed = 0
                motorist_injured = motorist_killed = 0
            
            # Select random streets
            streets = street_names[borough]
            on_street = random.choice(streets)
            cross_street = random.choice([s for s in streets if s != on_street])
            
            # Generate zip code (rough approximation)
            zip_codes = {
                'MANHATTAN': ['10001', '10002', '10003', '10004', '10005'],
                'BROOKLYN': ['11201', '11202', '11203', '11204', '11205'],
                'QUEENS': ['11375', '11377', '11378', '11379', '11380'],
                'BRONX': ['10451', '10452', '10453', '10454', '10455'],
                'STATEN ISLAND': ['10301', '10302', '10303', '10304', '10305'],
            }
            zip_code = random.choice(zip_codes[borough])
            
            crash_data = {
                'collision_id': base_collision_id + i,
                'crash_date': crash_date,
                'crash_time': crash_time,
                'latitude': lat,
                'longitude': lon,
                'borough': borough,
                'zip_code': zip_code,
                'on_street_name': on_street,
                'cross_street_name': cross_street,
                'off_street_name': '',
                'number_of_persons_injured': persons_injured,
                'number_of_persons_killed': persons_killed,
                'number_of_pedestrians_injured': pedestrians_injured,
                'number_of_pedestrians_killed': pedestrians_killed,
                'number_of_cyclist_injured': cyclist_injured,
                'number_of_cyclist_killed': cyclist_killed,
                'number_of_motorist_injured': motorist_injured,
                'number_of_motorist_killed': motorist_killed,
                'contributing_factor_vehicle_1': random.choice(contributing_factors),
                'contributing_factor_vehicle_2': random.choice(contributing_factors) if random.random() < 0.3 else '',
                'vehicle_type_code1': random.choice(vehicle_types),
                'vehicle_type_code2': random.choice(vehicle_types) if random.random() < 0.4 else '',
            }
            
            try:
                Crash.objects.create(**crash_data)
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} crashes...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating crash {i}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test crash records'
            )
        )
        
        # Display summary statistics
        total_crashes = Crash.objects.count()
        total_injured = Crash.objects.aggregate(
            total=models.Sum('number_of_persons_injured')
        )['total'] or 0
        total_killed = Crash.objects.aggregate(
            total=models.Sum('number_of_persons_killed')
        )['total'] or 0
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'Total crashes: {total_crashes}')
        self.stdout.write(f'Total injured: {total_injured}')
        self.stdout.write(f'Total killed: {total_killed}')
        
        # Borough breakdown
        from django.db.models import Count
        borough_stats = Crash.objects.values('borough').annotate(
            count=Count('collision_id')
        ).order_by('-count')
        
        self.stdout.write(f'\nBorough breakdown:')
        for stat in borough_stats:
            self.stdout.write(f'  {stat["borough"]}: {stat["count"]} crashes')
