import json
from tornado.web import RequestHandler
from ..utils.git import get_git_stats, reset_git_stats

class GitStatsHandler(RequestHandler):
    def get(self):
        sort_by = self.get_argument("sort", "total_ms")
        data = [
            {"cmd": "git " + " ".join(args),
             "count": int(s["count"]),
             "total_ms": round(s["total_ms"], 1),
             "max_ms": round(s["max_ms"], 1)}
            for args, s in get_git_stats(sort_by)
        ]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data, indent=2))

    def delete(self):
        reset_git_stats()
        self.set_status(204)
