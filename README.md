# Skeleton API data pull
# 1. The Local Configuration (.env)
You must update this local file for every new project to match your target API provider's domain and authentication credentials.

Change these values for each new provider
API_BASE_URL=
API_BEARER_TOKEN=
ensure secrets are updated in github options!

# 2. The Execution Target (app.py)
CHANGE THESE TWO LINES:
target_endpoint = "data1/data2/hello-world/issues"  # Your new target data
custom_parameters = {"state": "open", "per_page": 10} # Your new API filters :limit 10

# 3. CHANGE output_file="name_you_want.csv" also in the workflows

# 4. ALWAYS CHECK saving location options

# However, to make sure you never run into unexpected issues with a new project, 
watch out for these final two structural variations that differ between API providers
In Step 3, the code looks for a data key named "results" (records = data.get("results", data))
some might use custom names like "users", "items", or "records"
 If the resulting CSV is empty or formatted strangely, check the API's documentation and update that string key to match their exact structural layout.

Authorization Header Format
headers = {"Authorization": f"Bearer {API_TOKEN}"}
A small number of providers use custom authorization approaches instead:
They might require {"X-API-Key": f"{API_TOKEN}"} or They might just want {"Authorization": f"{API_TOKEN}"}
If an API returns a 401 Unauthorized error despite putting the correct token in your .env file, quickly check their documentation to see if they expect a unique header layout.

# Key Variations to Change for Different Projects
look at the while loop block and adjust three minor things:
1. The Page Key Name: Some APIs use {"page": 1}, others use {"p": 1} or {"pageNumber": 1}. Change page_params["page"] to match their key
2. The max_pages Safety Rail: Always keep a max_pages limit. If an API has a bug or you misconfigure a parameter, it prevents your program from running forever and draining your API limits or getting blocked
3. Switching to Offset: If the API uses offset-based pagination (e.g., page 1 is offset=0, page 2 is offset=10), change the math step at the bottom of the loop to increment by your limit size: current_offset += base_parameters["limit"]

# Important Daylight Saving Time (EDT) Note: update workflow to 0 4 * * * in Spring and 0 5 * * * in Fall
