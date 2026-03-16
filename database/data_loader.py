"""
Synthetic Data Loader
Loads CSV files and creates SQLite database for local development/testing
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json

class SyntheticDataLoader:
    """Load and manage synthetic data from CSV files"""
    
    def __init__(self, data_dir: str = None, db_path: str = "pharma_dev.db"):
        """
        Initialize the data loader
        
        Args:
            data_dir: Path to synthetic data directory
            db_path: Path to SQLite database file
        """
        if data_dir is None:
            # Try to find data directory
            current_dir = Path(__file__).parent.parent
            data_dir = current_dir / "data-generation" / "synthetic_data"
        
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.conn = None
        self.data = {}
        
        # Verify data directory exists
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Synthetic data directory not found: {self.data_dir}")
        
        print(f"✅ Data directory: {self.data_dir}")
    
    def load_csv_files(self):
        """Load all synthetic CSV files into pandas DataFrames"""
        
        csv_files = {
            "facilities": "facilities.csv",
            "medications": "medications.csv",
            "inventory": "inventory.csv",
            "consumption": "consumption.csv",
            "demand_forecast": "demand_forecast.csv",
            "transfers": "transfers.csv",
            "replenishment_orders": "replenishment_orders.csv",
            "external_signals": "external_signals.csv"
        }
        
        print("\n📂 Loading CSV Files...")
        print("-" * 60)
        
        for name, filename in csv_files.items():
            file_path = self.data_dir / filename
            
            if file_path.exists():
                try:
                    self.data[name] = pd.read_csv(file_path)
                    rows = len(self.data[name])
                    cols = len(self.data[name].columns)
                    print(f"✅ {name:25s} | {rows:8,d} rows | {cols:3d} columns")
                except Exception as e:
                    print(f"⚠️  {name:25s} | Error: {str(e)}")
            else:
                print(f"⚠️  {name:25s} | File not found")
        
        print("-" * 60)
        print(f"✅ Loaded {len(self.data)} tables\n")
        return self.data
    
    def create_sqlite_db(self):
        """Create SQLite database from loaded DataFrames"""
        
        print("📦 Creating SQLite Database...")
        print("-" * 60)
        
        self.conn = sqlite3.connect(str(self.db_path))
        
        for table_name, df in self.data.items():
            try:
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                print(f"✅ {table_name:25s} | {len(df):8,d} rows inserted")
            except Exception as e:
                print(f"❌ {table_name:25s} | Error: {str(e)}")
        
        self.conn.commit()
        
        print("-" * 60)
        print(f"✅ Database created: {self.db_path}\n")
    
    def get_connection(self):
        """Get SQLite connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
        return self.conn
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        return pd.read_sql_query(sql, self.get_connection())
    
    def get_summary_stats(self):
        """Print comprehensive summary statistics"""
        
        if not self.data:
            print("⚠️  No data loaded. Call load_csv_files() first.")
            return
        
        print("\n" + "="*70)
        print("SYNTHETIC DATA SUMMARY STATISTICS")
        print("="*70)
        
        # Facilities
        if "facilities" in self.data:
            df = self.data["facilities"]
            print(f"\n📍 FACILITIES ({len(df)} total)")
            print(f"   Location IDs: {', '.join(df['facility_id'].unique()[:3])}...")
            print(f"   Names: {', '.join(df['facility_name'].unique()[:3])}...")
            print(f"   Total storage capacity: {df['total_storage_capacity'].sum():,.0f} units")
        
        # Medications
        if "medications" in self.data:
            df = self.data["medications"]
            print(f"\n💊 MEDICATIONS ({len(df)} total)")
            print(f"   Categories: {', '.join(df['category'].unique()[:5])}...")
            print(f"   Average price: ${df['unit_cost'].mean():.2f}")
        
        # Inventory
        if "inventory" in self.data:
            df = self.data["inventory"]
            print(f"\n📦 INVENTORY BATCHES ({len(df)} total)")
            print(f"   Total units in stock: {df['quantity_on_hand'].sum():,.0f}")
            print(f"   Total inventory value: ${(df['quantity_on_hand'] * df['unit_cost']).sum():,.2f}")
            print(f"   Unique medications: {df['medication_id'].nunique()}")
            print(f"   Unique facilities: {df['facility_id'].nunique()}")
        
        # Consumption
        if "consumption" in self.data:
            df = self.data["consumption"]
            print(f"\n📊 CONSUMPTION HISTORY ({len(df)} records)")
            print(f"   Date range: {df['consumption_date'].min()} to {df['consumption_date'].max()}")
            print(f"   Total consumption: {df['quantity_consumed'].sum():,.0f} units")
            print(f"   Average daily consumption: {df['quantity_consumed'].mean():.2f} units")
        
        # Transfers
        if "transfers" in self.data:
            df = self.data["transfers"]
            print(f"\n🚚 TRANSFER HISTORY ({len(df)} transfers)")
            print(f"   Total units transferred: {df['quantity_transferred'].sum():,.0f}")
            print(f"   Date range: {df['transfer_date'].min()} to {df['transfer_date'].max()}")
        
        # Demand Forecasts
        if "demand_forecast" in self.data:
            df = self.data["demand_forecast"]
            print(f"\n📈 DEMAND FORECASTS ({len(df)} records)")
            print(f"   Date range: {df['forecast_date'].min()} to {df['forecast_date'].max()}")
        
        # External Signals
        if "external_signals" in self.data:
            df = self.data["external_signals"]
            print(f"\n🌡️  EXTERNAL SIGNALS ({len(df)} records)")
            print(f"   Date range: {df['signal_date'].min()} to {df['signal_date'].max()}")
        
        print("\n" + "="*70 + "\n")
    
    def get_expiring_items(self, days_threshold: int = 14) -> pd.DataFrame:
        """Get items expiring within threshold days"""
        
        inventory_df = self.data['inventory'].copy()
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'])
        
        today = datetime.now()
        inventory_df['days_to_expiry'] = (
            inventory_df['expiry_date'] - today
        ).dt.days
        
        expiring = inventory_df[
            inventory_df['days_to_expiry'] < days_threshold
        ].sort_values('days_to_expiry')
        
        return expiring
    
    def get_facility_capacity(self, facility_id: str) -> dict:
        """Get facility capacity info"""
        
        facilities_df = self.data['facilities']
        inventory_df = self.data['inventory']
        
        facility = facilities_df[
            facilities_df['facility_id'] == facility_id
        ].iloc[0]
        
        facility_inventory = inventory_df[
            inventory_df['facility_id'] == facility_id
        ]
        
        total_stock = facility_inventory['quantity_on_hand'].sum()
        total_capacity = facility['total_storage_capacity']
        utilization = (total_stock / total_capacity) * 100 if total_capacity > 0 else 0
        
        return {
            "facility_id": facility_id,
            "facility_name": facility['facility_name'],
            "total_capacity": int(total_capacity),
            "current_stock": int(total_stock),
            "utilization_percent": round(utilization, 2),
            "available_capacity": int(total_capacity - total_stock)
        }

# Create global instance
_loader = None

def get_data_loader(data_dir: str = None, db_path: str = "pharma_dev.db"):
    """Get or create SyntheticDataLoader instance"""
    global _loader
    if _loader is None:
        _loader = SyntheticDataLoader(data_dir, db_path)
    return _loader

if __name__ == "__main__":
    # Test data loader
    print("\n🔧 Testing SyntheticDataLoader\n")
    
    loader = SyntheticDataLoader()
    loader.load_csv_files()
    loader.create_sqlite_db()
    loader.get_summary_stats()
    
    # Test queries
    print("🧪 Test Queries:")
    print("-" * 70)
    
    # Find expiring items
    expiring = loader.get_expiring_items(14)
    print(f"\n✅ Found {len(expiring)} items expiring within 14 days")
    if len(expiring) > 0:
        print(f"   Sample: {expiring.iloc[0]['medication_id']} - {expiring.iloc[0]['days_to_expiry']} days")
    
    # Check facility capacity
    facilities = loader.data['facilities']['facility_id'].unique()
    if len(facilities) > 0:
        capacity = loader.get_facility_capacity(facilities[0])
        print(f"\n✅ Facility capacity: {capacity}")
    
    print("\n✅ All tests passed!\n")
