import time


class CheatingDetector:
    """Records cheating alerts from frontend MediaPipe analysis + OpenCV fallback."""

    WARMUP_MS = 25000

    def __init__(self):
        self.alerts = []
        self.analysis_count = 0
        self._start_time = time.time()
        self._no_face_active = False
        self._gaze_away_active = False
        self._multi_face_active = False
        self._tab_away_active = False
        self._phone_active = False

    def _warmup(self):
        return (time.time() - self._start_time) * 1000 < self.WARMUP_MS

    def _add_alert(self, atype, message, severity):
        self.alerts.append({
            "type": atype, "message": message,
            "severity": severity, "timestamp": time.time(),
        })

    def log_analysis(self, data: dict) -> dict:
        if self._warmup():
            return {"integrity_score": 100, "new_alerts": [], "warmup": True}

        self.analysis_count += 1
        new_alerts = []

        # Face detection
        face_detected = data.get("face_detected", True)
        if not face_detected and not self._no_face_active:
            self._no_face_active = True
            self._add_alert("NO_FACE", "Face not visible", "high")
            new_alerts.append(self.alerts[-1])
        elif face_detected and self._no_face_active:
            self._no_face_active = False

        # Gaze
        gaze = data.get("gaze_direction", "center")
        if gaze != "center" and not self._gaze_away_active:
            self._gaze_away_active = True
            self._add_alert("GAZE_AWAY", f"Looking {gaze}", "medium")
            new_alerts.append(self.alerts[-1])
        elif gaze == "center":
            self._gaze_away_active = False

        # Multiple faces
        faces_count = data.get("faces_count", 1)
        if faces_count > 1 and not self._multi_face_active:
            self._multi_face_active = True
            self._add_alert("MULTIPLE_FACES", f"{faces_count} faces in frame", "critical")
            new_alerts.append(self.alerts[-1])
        elif faces_count <= 1:
            self._multi_face_active = False

        # Tab switches
        tab_switches = data.get("tab_switches", 0)
        if tab_switches > 0 and not self._tab_away_active:
            self._tab_away_active = True
            self._add_alert("TAB_SWITCH", "Switched away from interview tab", "critical")
            new_alerts.append(self.alerts[-1])
        elif tab_switches == 0:
            self._tab_away_active = False

        # Phone / object near face
        phone_detected = data.get("phone_detected", False)
        if phone_detected and not self._phone_active:
            self._phone_active = True
            self._add_alert("PHONE_DETECTED", "Object near face detected", "high")
            new_alerts.append(self.alerts[-1])
        elif not phone_detected:
            self._phone_active = False

        integrity_score = max(0, 100 - (len(self.alerts) * 5))

        return {
            "face_detected": face_detected,
            "gaze_direction": gaze,
            "integrity_score": integrity_score,
            "total_alerts": len(self.alerts),
            "new_alerts": new_alerts,
        }

    def get_final_report(self) -> dict:
        alert_counts = {}
        for alert in self.alerts:
            t = alert["type"]
            alert_counts[t] = alert_counts.get(t, 0) + 1

        integrity_score = max(0, 100 - (len(self.alerts) * 5))

        risk_level = "LOW"
        if integrity_score < 80:
            risk_level = "MEDIUM"
        if integrity_score < 60:
            risk_level = "HIGH"
        if integrity_score < 40:
            risk_level = "CRITICAL"

        return {
            "integrity_score": integrity_score,
            "risk_level": risk_level,
            "total_alerts": len(self.alerts),
            "alert_breakdown": alert_counts,
            "all_alerts": self.alerts,
            "frames_analyzed": self.analysis_count,
        }
