from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import time
from datetime import datetime
from accidents.models import Crash

class Command(BaseCommand):
    help = 'Fetch crash data from NYC Open Data API'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=1000, help='Records per batch')
        parser.add_argument('--max-records', type=int, default=5000, help='Max total records')
        parser.add_argument('--api-key-id', type=str, help='Socrata API Key ID')
        parser.add_argument('--api-key-secret', type=str, help='Socrata API Key Secret')
    
    def handle(self, *args, **options):
        limit = options['limit']
        max_records = options['max_records']
        api_key_id = options.get('api_key_id')
        api_key_secret = options.get('api_key_secret')
        
        # API Configuration
        base_url = "https://data.cityofnewyork.us/api/v3/views/h9gi-nx95/query.json"
        
        # Headers for the request
        headers = {
            'Content-Type': 'application/json',
        }
        
        # HTTP Basic Auth with API key
        auth = None
        if api_key_id and api_key_secret:
            auth = (api_key_id, api_key_secret)
        
        # Fetch by date ranges to avoid pagination issues
        from datetime import datetime, timedelta
        
        # Start from a specific date (e.g., 2021-01-01)
        start_date = datetime(2021, 1, 1)
        end_date = start_date + timedelta(days=30)  # 30-day chunks
        
        total_fetched = 0
        
        while total_fetched < max_records:
            # Build the request payload with date filter
            payload = {
                'query': f"SELECT * WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND crash_date >= '{start_date.strftime('%Y-%m-%d')}' AND crash_date < '{end_date.strftime('%Y-%m-%d')}'",
                'page': {
                    'pageNumber': 1,
                    'pageSize': min(limit, max_records - total_fetched)
                },
                'includeSynthetic': False
            }
            
            self.stdout.write(f"Fetching records from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
            
            try:
                # Make API request
                response = requests.post(
                    base_url, 
                    headers=headers,
                    json=payload,
                    auth=auth,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    self.stdout.write("No more data available")
                    break
                
                # Process and save data
                saved_count = self.process_batch(data)
                total_fetched += saved_count
                
                self.stdout.write(f"Saved {saved_count} records. Total: {total_fetched}")
                
                # If we saved 0 records, move to next date range
                if saved_count == 0:
                    self.stdout.write("No new records in this date range. Moving to next period.")
                
                # Move to next date range
                start_date = end_date
                end_date = start_date + timedelta(days=30)
                
                # Rate limiting
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(f"API Error: {e}")
                break
    
    def process_batch(self, data):
        """Process a batch of records and save to database"""
        saved_count = 0
        
        with transaction.atomic():
            for record in data:
                try:
                    # Skip if collision_id already exists (avoid duplicates)
                    collision_id = int(record.get('collision_id', 0))
                    if Crash.objects.filter(collision_id=collision_id).exists():
                        continue
                    
                    # Create Crash object from API data
                    crash = Crash.objects.create(
                        collision_id=collision_id,
                        crash_date=self.parse_date(record.get('crash_date')),
                        crash_time=record.get('crash_time', ''),
                        latitude=float(record.get('latitude', 0)),
                        longitude=float(record.get('longitude', 0)),
                        borough=record.get('borough', ''),
                        zip_code=record.get('zip_code', ''),
                        on_street_name=record.get('on_street_name', ''),
                        cross_street_name=record.get('cross_street_name', ''),
                        off_street_name=record.get('off_street_name', ''),
                        number_of_persons_injured=int(record.get('number_of_persons_injured', 0)),
                        number_of_persons_killed=int(record.get('number_of_persons_killed', 0)),
                        number_of_pedestrians_injured=int(record.get('number_of_pedestrians_injured', 0)),
                        number_of_pedestrians_killed=int(record.get('number_of_pedestrians_killed', 0)),
                        number_of_cyclist_injured=int(record.get('number_of_cyclist_injured', 0)),
                        number_of_cyclist_killed=int(record.get('number_of_cyclist_killed', 0)),
                        number_of_motorist_injured=int(record.get('number_of_motorist_injured', 0)),
                        number_of_motorist_killed=int(record.get('number_of_motorist_killed', 0)),
                        contributing_factor_vehicle_1=record.get('contributing_factor_vehicle_1', ''),
                        contributing_factor_vehicle_2=record.get('contributing_factor_vehicle_2', ''),
                        contributing_factor_vehicle_3=record.get('contributing_factor_vehicle_3', ''),
                        contributing_factor_vehicle_4=record.get('contributing_factor_vehicle_4', ''),
                        contributing_factor_vehicle_5=record.get('contributing_factor_vehicle_5', ''),
                        vehicle_type_code1=record.get('vehicle_type_code1', ''),
                        vehicle_type_code2=record.get('vehicle_type_code2', ''),
                        vehicle_type_code_3=record.get('vehicle_type_code_3', ''),
                        vehicle_type_code_4=record.get('vehicle_type_code_4', ''),
                        vehicle_type_code_5=record.get('vehicle_type_code_5', ''),
                    )
                    saved_count += 1
                    
                except (ValueError, KeyError) as e:
                    # Skip invalid records
                    self.stdout.write(f"Skipping invalid record: {e}")
                    continue
        
        return saved_count
    
    def parse_date(self, date_string):
        """Parse NYC API date format"""
        if not date_string:
            return datetime.now()
        
        try:
            # Handle different date formats from NYC API
            if 'T' in date_string:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_string, '%Y-%m-%d')
        except:
            return datetime.now()