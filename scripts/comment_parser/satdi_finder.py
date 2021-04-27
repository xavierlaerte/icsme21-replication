import requests
import time

def run_query(json, headers): # A simple function to use requests.post to make the API call. 

    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))

#main    
def get_satdi(owner, name, label):                           
    repo_owner = '"' + owner + '"'
    repo_name = '"' + name + '"'
    label = '"' + label + '"'
    #repo_owner = '"admitd"'
    #repo_name =  '"satd_test"'
    #label = '"technical debt"'

    query = """
    query{
        repository(owner:{OWNER} name:{NAME}){
            issues(first:100{AFTER}, labels:{LABEL}){
                pageInfo{
                    hasNextPage
                    endCursor
                }
                nodes{
                    number
                }
            }
        }
        rateLimit{
            remaining
            resetAt
        }
    }   
    """
    query_with_owner = query.replace("{OWNER}", repo_owner)
    query_with_name = query_with_owner.replace("{NAME}", repo_name)
    query_with_label = query_with_name.replace("{LABEL}", label)
    final_query = query_with_label.replace("{AFTER}", "")

    json = {
        "query":final_query, "variables":{}
    }

    token = '0cc12d6d1c36edf67de22296213a08b284f462ec' #token laerte
    headers = {"Authorization": "Bearer " + token}

    result = run_query(json, headers)
    #print(result)
    nodes = result['data']['repository']['issues']['nodes']
    next_page  = result['data']['repository']['issues']['pageInfo']['hasNextPage']

    while(next_page):
        print("PAGINATING")
        if(result['data']['rateLimit']['remaining'] == 0):
            token = '788ebfa5341cc56aa096b8afb32295b3fb1fd540'
            headers = {"Authorization": "Bearer " + token}

        cursor = result['data']['repository']['issues']['pageInfo']['endCursor'] 
        next_query = query_with_label.replace("{AFTER}", ", after: \"%s\"" % cursor) 
        json["query"] = next_query
        result = run_query(json, headers)         
        nodes += result['data']['repository']['issues']['nodes']
        next_page  = result['data']['repository']['issues']['pageInfo']['hasNextPage']
        
    result = []
    for issue in nodes:
        result.append(issue['number'])
    
    return result

if __name__ == "__main__":
    out = get_satdi("laertexavier", "satd_test", "technical debt")
    print(str(len(out)))        
    print(out)