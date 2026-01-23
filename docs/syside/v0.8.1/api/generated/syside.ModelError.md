<div id="syside-modelerror" class="section">

# syside.ModelError[](#syside-modelerror "Link to this heading")

  - *<span class="pre">exception</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ModelError</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">model</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Model</span>](/v0.8.1/api/generated/syside.Model.md "syside.Model")</span>*, *<span class="n"><span class="pre">diagnostics</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Diagnostics</span>](/v0.8.1/api/generated/syside.Diagnostics.md "syside.Diagnostics")</span>*<span class="sig-paren">)</span>[](#syside.ModelError "Link to this definition")  
    Bases: `RuntimeError`
    
    An exception thrown when model contains errors.
    
    Initialization
    
    Initialize self. See help(type(self)) for accurate signature.
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.ModelError.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_cause\_\_</span></span>[](#syside.ModelError.__cause__ "Link to this definition")  
        exception cause
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_context\_\_</span></span>[](#syside.ModelError.__context__ "Link to this definition")  
        exception context
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_delattr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__delattr__ "Link to this definition")  
        Implement delattr(self, name).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__dir__ "Link to this definition")  
        Default dir() implementation.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_eq\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__eq__ "Link to this definition")  
        Return self==value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__format__ "Link to this definition")  
        Default object formatter.
        
        Return str(self) if format\_spec is empty. Raise TypeError otherwise.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ge\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__ge__ "Link to this definition")  
        Return self\>=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getattribute\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__getattribute__ "Link to this definition")  
        Return getattr(self, name).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getstate\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__getstate__ "Link to this definition")  
        Helper for pickle.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_gt\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__gt__ "Link to this definition")  
        Return self\>value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__hash__ "Link to this definition")  
        Return hash(self).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_le\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__le__ "Link to this definition")  
        Return self\<=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_lt\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__lt__ "Link to this definition")  
        Return self\<value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ne\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__ne__ "Link to this definition")  
        Return self\!=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__new__ "Link to this definition")  
        Create and return a new object. See help(type) for accurate signature.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__reduce__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__reduce_ex__ "Link to this definition")  
        Helper for pickle.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__repr__ "Link to this definition")  
        Return repr(self).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_setattr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__setattr__ "Link to this definition")  
        Implement setattr(self, name, value).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_setstate\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__setstate__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_sizeof\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__sizeof__ "Link to this definition")  
        Size of object in memory, in bytes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_subclasshook\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.__subclasshook__ "Link to this definition")  
        Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.\_\_subclasscheck\_\_(). It should return True, False or NotImplemented. If it returns NotImplemented, the normal algorithm is used. Otherwise, it overrides the normal algorithm (and the outcome is cached).
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_suppress\_context\_\_</span></span>[](#syside.ModelError.__suppress_context__ "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_traceback\_\_</span></span>[](#syside.ModelError.__traceback__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">add\_note</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.add_note "Link to this definition")  
        Exception.add\_note(note) – add a note to the exception
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">args</span></span>[](#syside.ModelError.args "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">with\_traceback</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ModelError.with_traceback "Link to this definition")  
        Exception.with\_traceback(tb) – set self.\_\_traceback\_\_ to tb and return self.

</div>
