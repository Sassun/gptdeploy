from langchain import PromptTemplate

from src.constants import IMPLEMENTATION_FILE_NAME

general_guidelines_string = '''The code you write is production ready. Every file starts with comments describing what the code is doing before the first import. Comments can only be written within code blocks.
Then all imports are listed.

Start from top-level and then fully implement all methods.'''


not_allowed_docker_string = '''Note that the Dockerfile only has access to the files: microservice.py, requirements.txt, config.yml, test_microservice.py.
Note that the Dockerfile runs the test_microservice.py during the build process.
The Dockerfile must not attach a virtual display when running test_microservice.py.'''


not_allowed_function_string = '''The implemented function and the test must not use the GPU.
The implemented function and the test must not access a database.
The implemented function and the test must not access a display.
The implemented function and the test must not access external apis except unless it is explicitly mentioned in the description or test case (e.g. by mentioning the api that should be used or by providing a URL to access the data). 
The implemented function and the test must not load data from the local file system unless it was created by the implemented function itself.
The implemented function and the test must not use a pre-trained model unless it is explicitly mentioned in the description.
The implemented function and the test must not train a model.
The implemented function and the test must not contain prototype or placeholder implementations.
The implemented function and the test must run in a docker container based on debian.
The implemented function and the test must not use libraries like Flask.
The implemented function and the test must not have a __main__ function.
The implemented function and the test must use gpt_3_5_turbo_api if the task requires understanding or generation of natural language or using any language model. Other language models are not allowed.
The implemented function and the test must not use gpt_3_5_turbo_api or any other language model if the task does not require understanding or generation of natural language.'''


template_generate_microservice_name = PromptTemplate.from_template(
    '''Generate a name for the executor matching the description:
"{description}"
The executor name must fulfill the following criteria:
- camel case
- start with a capital letter
- only consists of lower and upper case characters
- end with Executor.

The output is a the raw string wrapped into ``` and starting with **name.txt** like this:
**name.txt**
```
PDFParserExecutor
```'''
)


template_generate_possible_packages_output_format_string = '''You must output the package combinations as a list of lists wrapped into ``` and name it **packages.csv**. Do not use quotation marks around packages names in the output. Separate packages in a combination by comma. The output looks this:
**{file_name}**
```
package1a, package1b ...
package2a, package2b, package2c
package3a ...
package4a ...
package5a ...
...
```'''


template_generate_possible_packages = PromptTemplate.from_template(
    '''Here is the task description of the problem you need to solve:
"{description}"
1. Write down the different strategies to solve the task. For each strategy write down all the non-trivial subtasks you need to solve. If there is a natural language understanding or generation stragegy, write it down.
2. Find out what is the core problem to solve.
3. List up to 15 Python packages that are specifically designed or have functionalities to solve the complete core problem with one of the defined strategies. You must add gpt_3_5_turbo_api if the task involves generating or understanding natural language or using a (pre-trained) language model.
4. Exclude any package that can generate or understand natural language or enables using any language model, but you must not exclude gpt_3_5_turbo_api. Print the cleaned list of packages and give a brief reason for keeping it after its name.
5. For each cleaned package think if it fulfills the following requirements:
a) specifically designed or have functionalities to solve the complete core problem.
b) has a stable api among different versions
c) does not have system requirements
d) can solve the task when running in a docker container
e) the implementation of the core problem using the package would obey the following rules:
''' + not_allowed_function_string + '''

When answering, just write "yes" or "no".

6. Determine the 5 most suitable python package combinations, ordered from the best to the least suitable. Combine the packages to achieve a comprehensive solution.
If the package is mentioned in the description, then it is automatically the best one.
If you listed gpt_3_5_turbo_api earlier, you must use it. gpt_3_5_turbo_api is the best package for handling text-based tasks. Also, gpt_3_5_turbo_api doesn't need any other packages processing text or using language models. It can handle any text-based task alone.

''' + template_generate_possible_packages_output_format_string)


template_code_wrapping_string = '''The code will go into {file_name_purpose}. Make sure to wrap the code into ``` marks even if you only output code:
**{file_name}**
```{tag_name}
...code...
```
You must provide the complete file with the exact same syntax to wrap the code.'''


gpt_35_turbo_usage_string = """If need to use gpt_3_5_turbo_api, then this is an example on how to use it:
```
from .apis import GPT_3_5_Turbo_API

gpt_3_5_turbo_api = GPT_3_5_Turbo_API(
    system=\'\'\'
You are a tv-reporter who is specialized in C-list celebrities.
When you get asked something like 'Who was having a date with <X>?', then you answer with a json like '{{"dates": ["<Y>", "<Z>"]}}'. 
You must not answer something else - only the json.
\'\'\')

response_string = gpt(prompt)  # fill-in the prompt (str); the output is a string
```
"""


template_generate_function = PromptTemplate.from_template(
    general_guidelines_string + '''

Write a python function which receives as input a dictionary and outputs a dictionary. The function is called 'func'.
The function must full-fill: '{microservice_description}'.
It will be tested with the following scenario: '{test_description}'.
For the implementation use the following package(s): '{packages}'.

Obey the following rules:
''' + not_allowed_function_string + '''

Your approach:
1. Identify the core challenge when implementing the function.
2. Think about solutions for these challenges. If gpt_3_5_turbo_api is mentioned in the above list of packages, then you must use it.
3. Decide for one of the solutions.
4. Write the code for the function. Don't write code for the test.
''' + gpt_35_turbo_usage_string + '\n' + template_code_wrapping_string
)


template_generate_test = PromptTemplate.from_template(
    general_guidelines_string + '''

{code_files_wrapped}

Write a single pytest case that tests the following scenario: '{test_description}'. In case the test scenario is not precise enough, test a general case without any assumptions.
Start the test with an extensive comment about the test case. If gpt_3_5_turbo_api is used in the executor, then the test must not check the exact output of the executor as it is not deterministic. 

Use the following import to import the function:
```
from .implementation import func
```

''' + not_allowed_function_string + '''
The test must not open local files.
The test must not mock a function of the executor.
The test must not use other data than the one provided in the test scenario.
The test must not set any environment variables which require a key.
''' + '\n' + template_code_wrapping_string
)


template_generate_requirements = PromptTemplate.from_template(
    general_guidelines_string + '''

{code_files_wrapped}
    
Write the content of the requirements.txt file.
The requirements.txt file must include the following packages in that specified version:
```
jina==3.15.1.dev14
docarray==0.21.0
openai>=0.26.0
pytest
```
Add any more packages that are needed to run the code.
You must not add gpt_3_5_turbo_api to the requirements.txt file. 

All versions are fixed using ~=, ==, <, >, <=, >=. The package versions must not have conflicts. Output only the requirements.txt file.
''' + '\n' + template_code_wrapping_string
)


template_generate_apt_get_install = PromptTemplate.from_template(
    '''Given the following Dockerfile:

{docker_file_wrapped}

Name all packages which need to be installed via `apt-get install` in above Dockerfile (`{{apt_get_packages}}`) for the following requirements.txt file:

{requirements_file_wrapped}

Output them as a white space separated list:'''
)


template_summarize_error = PromptTemplate.from_template(
    '''Here is an error message I encountered during the docker build process:
"{error}"
Your task is to summarize the error message as compact and informative as possible while maintaining all information necessary to debug the core issue.
Warnings are not worth mentioning.'''
)


template_is_dependency_issue = PromptTemplate.from_template(
    '''Your task is to assist in identifying the root cause of a Docker build error for a python application.
The error message is as follows:

{summarized_error}

You are given the following files:

{all_files_string}

Is this a PACKAGE_MANAGER dependency installation failure? Answer with "yes" or "no".'''
)


template_solve_pip_dependency_issue = PromptTemplate.from_template(
    '''Your task is to provide guidance on how to solve an error that occurred during the Docker build process. 
Here is the summary of the error that occurred:
{summarized_error}

To solve this error, you should:
1. Suggest 3 to 5 possible solutions on how to solve it. You have no access to the documentation of the package.
2. Decide for the best solution and explain it in detail.
3. Write down how requirements.txt should look like to solve the error. 
For files that need to be changed, you must provide the complete file with the exact same syntax to wrap the code.

You are given the following files:

{all_files_string}

Output how the requirements.txt file should look like to solve the error.
If you output a file, then write the complete file. Use the exact following syntax to wrap the code:

**requirements.txt**
```
...packages...
```

Example:

**requirements.txt**
```
jina==2.0.0
```
'''
)


template_solve_apt_get_dependency_issue = PromptTemplate.from_template(
    '''Your task is to provide guidance on how to solve an error that occurred during the Docker build process. 
Here is the summary of the error that occurred:
{summarized_error}

You are given the following files:

{all_files_string}

To solve this error, you should determine the list of packages that need to be installed via `apt-get install` in the Dockerfile.
Output them as a white space separated list:'''
)


template_solve_code_issue = PromptTemplate.from_template(
    '''General rules:
''' + not_allowed_function_string + '''

Here is the description of the task the function must solve:
{task_description}

Here is the test scenario the function must pass:
{test_description}
Here are all the files I use:
{all_files_string}


Here is the summary of the error that occurred:
{summarized_error}

To solve this error, you should:
1. Suggest 3 to 5 possible solutions on how to solve it. You have no access to the documentation of the package.
2. Decide for the best solution and explain it in detail.
3. Write down the files that need to be changed, but not files that don't need to be changed.
Note that any changes needed to make the test pass must be written under the constraint that ''' + IMPLEMENTATION_FILE_NAME +  ''' will be used in a different file as well.
Obey the following rules:
''' + f'{not_allowed_function_string}\n{not_allowed_docker_string}\n{gpt_35_turbo_usage_string}' + '''

Output all the files that need change. You must not change the Dockerfile. 
Don't output files that don't need change. If you output a file, then write the complete file.
Use the exact following syntax to wrap the code:

**...**
```...
...code...
```

Example:

**microservice.py**
```python
print('hello world')
```'''
)


template_generate_playground = PromptTemplate.from_template(
    general_guidelines_string + '''👨‍💻

{code_files_wrapped}

Create a playground for the executor {microservice_name} using streamlit.
The playground must look like it was made by a professional designer.
All the ui elements are well thought out to make them visually appealing and easy to use.
Don't mention the word Playground in the title.
The playground contains many emojis that fit the theme of the playground and has an emoji as favicon.
The playground encourages the user to deploy their own microservice by clicking on this link: https://github.com/jina-ai/gptdeploy
The playground uses the following code to send a request to the microservice:
```
from jina import Client, Document, DocumentArray
client = Client(host='http://localhost:8080')
d = Document(text=json.dumps(INPUT_DICTIONARY)) # fill-in dictionary which takes input
response = client.post('/', inputs=DocumentArray([d])) # always use '/'
print(response[0].text) # can also be blob in case of image/audio..., this should be visualized in the streamlit app
```
Note that the response will always be in response[0].text
The playground displays a code block containing the microservice specific curl code that can be used to send the request to the microservice.
While the exact payload in the curl might change, the host and deployment ID always stay the same. Example: 
```
deployment_id = os.environ.get("K8S_NAMESPACE_NAME", "")
host = f'https://gptdeploy-{{deployment_id.split("-")[1]}}.wolf.jina.ai/post' if deployment_id else "http://localhost:8080/post"
with st.expander("See curl command"):
    st.code(
        f'curl -X \\'POST\\' \\'host\\' -H \\'accept: application/json\\' -H \\'Content-Type: application/json\\' -d \\'{{{{"data": [{{{{"text": "hello, world!"}}}}]}}}}\\'',
        language='bash'
    )
```
You must provide the complete app.py file using the following syntax to wrap the code:
**app.py**
```python
...
```
The playground (app.py) must always use the host on http://localhost:8080  and must not let the user configure the host on the UI.
The playground (app.py) must not import the executor.
'''
)


template_chain_of_thought = PromptTemplate.from_template(
    '''First, write down an extensive list of obvious and non-obvious observations about {file_name_purpose} that could need an adjustment. Explain why.
Think if all the changes are required and finally decide for the changes you want to make, but you are not allowed disregard the instructions in the previous message.
Be very hesitant to change the code. Only make a change if you are sure that it is necessary.

Output only {file_name_purpose}
Write the whole content of {file_name_purpose} - even if you decided to change only a small thing or even nothing.
''' + '\n' + template_code_wrapping_string + '''

Remember: 
The playground (app.py) must always use the host on http://localhost:8080 and must not let the user configure the host on the UI.
The playground (app.py) must not import the executor.
'''
)

# Create a wrapper around google called Joogle. It modifies the page summary preview text of the search results to insert the word Jina as much as possible.
template_refinement = PromptTemplate.from_template(
    '''
1.Quickly go through the checklist (input/output well defined? api or db access needed?)  and think about if you should ask something to the client or if you should write the final description.
**client-response.txt**
```text
{user_input}
```
2.Either write the prompt.txt or the final.txt file.
Either ask for clarification like this:
**prompt.txt**
```text
<prompt to the client here (must be only one question)>
```

Or write the summarized microservice{_optional_test} description like this:
**final.txt**
```text
<microservice{_optional_test} description here>
```
Note that your response must be either prompt.txt or final.txt. You must not write both.
Note that you must obey the double asterisk and tripple backtick syntax from above.
Note that prompt.txt must not only contain one question.
Note that if urls, secrets, database names, etc. are mentioned, they must be part of the summary.
'''
)
