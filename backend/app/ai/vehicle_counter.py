from typing import List, Tuple, Set

class GateVehicleCounter:
    """
    Line-crossing vehicle counter for gate camera pipeline streams.
    Tracks vehicle bounding box centroids across virtual ROI counting line.
    """
    def __init__(self, gate_id: str, count_line_y: int = 300):
        self.gate_id = gate_id
        self.count_line_y = count_line_y
        self.tracked_vehicle_ids: Set[int] = set()
        self.total_count = 0

    def update_vehicle_tracks(self, vehicle_detections: List[Tuple[int, Tuple[int, int, int, int]]]) -> int:
        """
        Updates tracked vehicle positions and increments count when a vehicle crosses the ROI line.
        
        Args:
            vehicle_detections: List of tuples (track_id, (x1, y1, x2, y2))
            
        Returns:
            int: Updated total vehicle count at this gate.
        """
        for track_id, bbox in vehicle_detections:
            x1, y1, x2, y2 = bbox
            cy = (y1 + y2) // 2

            # Check if vehicle centroid crosses the ROI counting line
            if cy >= self.count_line_y and track_id not in self.tracked_vehicle_ids:
                self.tracked_vehicle_ids.add(track_id)
                self.total_count += 1

        return self.total_count
