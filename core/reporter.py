import time
import os
import csv

class ReportGenerator:
    def generate(self, job_mgr, total_bytes, stream_count=4, strategy_name="Unknown"):
        start = job_mgr.progress_data.get("start_time", time.time())
        end = time.time()
        duration = end - start
        
        # Calculate stats
        avg_speed = 0
        if duration > 0:
            avg_speed = (total_bytes / (1024*1024)) / duration # MB/s
        
        size_gb = total_bytes / (1024*1024*1024)
        
        # 1. TEXT REPORT (For the Client)
        lines = [
            "========================================",
            "      GEEK SQUAD TRANSFER REPORT        ",
            "========================================",
            f"Date:       {time.ctime()}",
            f"Strategy:   {strategy_name}",
            f"Streams:    {stream_count}",
            "----------------------------------------",
            f"Source:     {job_mgr.job_data['src']}",
            f"Total Data: {size_gb:.2f} GB",
            f"Total Time: {duration/60:.1f} Minutes",
            f"Avg Speed:  {avg_speed:.2f} MB/s",
            "----------------------------------------",
            f"Status:     {job_mgr.progress_data.get('status', 'Unknown')}",
            "========================================",
        ]
        
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        txt_path = os.path.join(desktop, "Transfer_Report_Client.txt")
        with open(txt_path, "w") as f:
            f.write("\n".join(lines))

        # 2. CSV ANALYTICS (For You - The Data Nerd)
        csv_path = os.path.join(desktop, "GS_Transfer_Analytics_Master.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, "a", newline="") as csvfile:
            headers = ["Date", "Strategy", "Streams", "Total_GB", "Time_Sec", "Speed_MBs", "Source_Path"]
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                "Date": time.ctime(),
                "Strategy": strategy_name,
                "Streams": stream_count,
                "Total_GB": round(size_gb, 4),
                "Time_Sec": round(duration, 2),
                "Speed_MBs": round(avg_speed, 2),
                "Source_Path": job_mgr.job_data['src']
            })
            
        return txt_path, csv_path