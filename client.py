from scope import Scope


class NoopClient:
    def __repr__(self):
        return "<{} id={}>".format(self.__class__.__name__, id(self))
    
    def get_integration(name_or_class):
        return None
    
    def should_send_default_pii():
        return False


class Client(NoopClient):
    def __repr__(self):
        return "<{} id={}>".format(self.__class__.__name__, id(self))
    
    @classmethod
    def get_client(cls):
        client = Scope.get_current_scope().client
        if client is not None:
            return client
        
        client = Scope.get_isolation_scope().client  
        if client is not None:
            return client
        
        client = Scope.get_global_scope().client
        if client is not None:
            return client
        
        return NoopClient()

