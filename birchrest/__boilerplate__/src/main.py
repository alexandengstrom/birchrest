from birchrest import BirchRest

app = BirchRest(log_level="debug")
app.serve(port=6247)