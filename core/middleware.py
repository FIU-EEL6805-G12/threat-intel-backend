class VictimMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == "GET" and request.path.startswith("/api/"):
            victim_id = view_kwargs.get("victim_id")
            victim = Victim.objects.get(id=victim_id)
            victim.last_seen = datetime.now()
            victim.save()
