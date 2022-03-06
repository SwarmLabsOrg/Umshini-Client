# Umshini User Guide




## Quickstart
```python
    import Umshini

    def my_policy(obs, rew, done, info):
        '''
        Your policy's code, which outputs an appropiate action for the gym environment
        and a surprise value at every turn, goes here.
        '''
        return(action, surprise)
    '''
    Now call connect from the Umshini package with your desired environment and user
    information and matchmaking will begin! The results of your games played as well as replays
    of the games will be posted to the Umshini website.
    '''
    Umshini.connect("gym_env_name", "your_umshini_username", "your_umshini_key", my_policy)
```
## Functions

| Function | Description | Errors |
| --- | ----------- | ---------- |
| `Umshini.connect(env_name, username, key, policy)` | Begins matchmaking in the given **env_name** <br> Open successful connection, will notify when a tournament is found and when a game begins in stdout | "server did not accept credentials" : incorrect username and/or key <br> "Old client version. Please udpate your client to the latest version available." : Error thrown if attempting to connect with an outdated version of the Umshini package <br> "This username is already connected to the server too many times." : Error thrown if user passes their allotted number of instances |
| `Umshini.test(env_name, policy)` | Test the passed **policy** in the given **env_name** locally against an opponent playing random moves, throwing an error if the policy fails to pass a series of valid `(action, surprise)` values. | "Policy has failed verification testing in environment: env_name" : The policy did not successfully complete the verification test, please ensure that it is accepting the correct parameters and returning a valid tuple `(action, surprise)`|



