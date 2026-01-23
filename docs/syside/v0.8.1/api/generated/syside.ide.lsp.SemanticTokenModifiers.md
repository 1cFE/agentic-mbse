<div id="syside-ide-lsp-semantictokenmodifiers" class="section">

# syside.ide.lsp.SemanticTokenModifiers[](#syside-ide-lsp-semantictokenmodifiers "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">SemanticTokenModifiers</span></span>[](#syside.ide.lsp.SemanticTokenModifiers "Link to this definition")  
    Bases: `enum.IntFlag`
    
    LSP defined semantic token modifiers. Technically, this is not a flag enum but `nanobind` does not permit arbitrary values otherwise.
    
    See [LSP specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokenModifiers) and [VS Code docs](https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide#standard-token-types-and-modifiers) for more details.
    
    Initialization
    
    Initialize self. See help(type(self)) for accurate signature.
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.ide.lsp.SemanticTokenModifiers.__repr__ "Link to this definition")  
        Return repr(self).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">None</span>*[](#syside.ide.lsp.SemanticTokenModifiers.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Declaration</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Declaration "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Definition</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Definition "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Readonly</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Readonly "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Static</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">3</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Static "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Deprecated</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">4</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Deprecated "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Abstract</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">5</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Abstract "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Async</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">6</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Async "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Modification</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">7</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Modification "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Documentation</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">8</span>*[](#syside.ide.lsp.SemanticTokenModifiers.Documentation "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">DefaultLibrary</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">9</span>*[](#syside.ide.lsp.SemanticTokenModifiers.DefaultLibrary "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_abs\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__abs__ "Link to this definition")  
        abs(self)
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_add\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__add__ "Link to this definition")  
        Return self+value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_and\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__and__ "Link to this definition")  
        Return self\&value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_bool\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__bool__ "Link to this definition")  
        True if self else False
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ceil\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__ceil__ "Link to this definition")  
        Ceiling of an Integral returns itself.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_delattr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__delattr__ "Link to this definition")  
        Implement delattr(self, name).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__dir__ "Link to this definition")  
        Default dir() implementation.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_divmod\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__divmod__ "Link to this definition")  
        Return divmod(self, value).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_eq\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__eq__ "Link to this definition")  
        Return self==value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_float\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__float__ "Link to this definition")  
        float(self)
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_floor\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__floor__ "Link to this definition")  
        Flooring an Integral returns itself.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_floordiv\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__floordiv__ "Link to this definition")  
        Return self//value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__format__ "Link to this definition")  
        Convert to a string according to format\_spec.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ge\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__ge__ "Link to this definition")  
        Return self\>=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getattribute\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__getattribute__ "Link to this definition")  
        Return getattr(self, name).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getnewargs\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__getnewargs__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_getstate\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__getstate__ "Link to this definition")  
        Helper for pickle.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_gt\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__gt__ "Link to this definition")  
        Return self\>value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__hash__ "Link to this definition")  
        Return hash(self).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_index\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__index__ "Link to this definition")  
        Return self converted to an integer, if self is suitable for use as an index into a list.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_int\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__int__ "Link to this definition")  
        int(self)
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_invert\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__invert__ "Link to this definition")  
        \~self
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_le\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__le__ "Link to this definition")  
        Return self\<=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_lshift\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__lshift__ "Link to this definition")  
        Return self\<\<value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_lt\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__lt__ "Link to this definition")  
        Return self\<value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_mod\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__mod__ "Link to this definition")  
        Return self%value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_mul\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__mul__ "Link to this definition")  
        Return self\*value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ne\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__ne__ "Link to this definition")  
        Return self\!=value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_neg\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__neg__ "Link to this definition")  
        \-self
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__new__ "Link to this definition")  
        Create and return a new object. See help(type) for accurate signature.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_or\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__or__ "Link to this definition")  
        Return self|value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_pos\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__pos__ "Link to this definition")  
        \+self
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_pow\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__pow__ "Link to this definition")  
        Return pow(self, value, mod).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_radd\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__radd__ "Link to this definition")  
        Return value+self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rand\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rand__ "Link to this definition")  
        Return value\&self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rdivmod\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rdivmod__ "Link to this definition")  
        Return divmod(value, self).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__reduce__ "Link to this definition")  
        Helper for pickle.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__reduce_ex__ "Link to this definition")  
        Helper for pickle.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rfloordiv\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rfloordiv__ "Link to this definition")  
        Return value//self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rlshift\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rlshift__ "Link to this definition")  
        Return value\<\<self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rmod\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rmod__ "Link to this definition")  
        Return value%self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rmul\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rmul__ "Link to this definition")  
        Return value\*self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_ror\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__ror__ "Link to this definition")  
        Return value|self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_round\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__round__ "Link to this definition")  
        Rounding an Integral returns itself.
        
        Rounding with an ndigits argument also returns an integer.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rpow\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rpow__ "Link to this definition")  
        Return pow(value, self, mod).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rrshift\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rrshift__ "Link to this definition")  
        Return value\>\>self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rshift\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rshift__ "Link to this definition")  
        Return self\>\>value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rsub\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rsub__ "Link to this definition")  
        Return value-self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rtruediv\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rtruediv__ "Link to this definition")  
        Return value/self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_rxor\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__rxor__ "Link to this definition")  
        Return value^self.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_setattr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__setattr__ "Link to this definition")  
        Implement setattr(self, name, value).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_sizeof\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__sizeof__ "Link to this definition")  
        Returns size in memory, in bytes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_sub\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__sub__ "Link to this definition")  
        Return self-value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_subclasshook\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__subclasshook__ "Link to this definition")  
        Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.\_\_subclasscheck\_\_(). It should return True, False or NotImplemented. If it returns NotImplemented, the normal algorithm is used. Otherwise, it overrides the normal algorithm (and the outcome is cached).
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_truediv\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__truediv__ "Link to this definition")  
        Return self/value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_trunc\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__trunc__ "Link to this definition")  
        Truncating an Integral returns itself.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_xor\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__xor__ "Link to this definition")  
        Return self^value.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">as\_integer\_ratio</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.as_integer_ratio "Link to this definition")  
        Return a pair of integers, whose ratio is equal to the original int.
        
        The ratio is in lowest terms and has a positive denominator.
        
        <div class="doctest highlight-default notranslate">
        
        <div class="highlight">
        
            >>> (10).as_integer_ratio()
            (10, 1)
            >>> (-10).as_integer_ratio()
            (-10, 1)
            >>> (0).as_integer_ratio()
            (0, 1)
        
        </div>
        
        </div>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">bit\_count</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.bit_count "Link to this definition")  
        Number of ones in the binary representation of the absolute value of self.
        
        Also known as the population count.
        
        <div class="doctest highlight-default notranslate">
        
        <div class="highlight">
        
            >>> bin(13)
            '0b1101'
            >>> (13).bit_count()
            3
        
        </div>
        
        </div>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">bit\_length</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.bit_length "Link to this definition")  
        Number of bits necessary to represent self in binary.
        
        <div class="doctest highlight-default notranslate">
        
        <div class="highlight">
        
            >>> bin(37)
            '0b100101'
            >>> (37).bit_length()
            6
        
        </div>
        
        </div>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">conjugate</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.conjugate "Link to this definition")  
        Returns self, the complex conjugate of any int.
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">denominator</span></span>[](#syside.ide.lsp.SemanticTokenModifiers.denominator "Link to this definition")  
        the denominator of a rational number in lowest terms
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">imag</span></span>[](#syside.ide.lsp.SemanticTokenModifiers.imag "Link to this definition")  
        the imaginary part of a complex number
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">is\_integer</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.is_integer "Link to this definition")  
        Returns True. Exists for duck type compatibility with float.is\_integer.
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">numerator</span></span>[](#syside.ide.lsp.SemanticTokenModifiers.numerator "Link to this definition")  
        the numerator of a rational number in lowest terms
    
    <!-- end list -->
    
      - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">real</span></span>[](#syside.ide.lsp.SemanticTokenModifiers.real "Link to this definition")  
        the real part of a complex number
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">to\_bytes</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.to_bytes "Link to this definition")  
        Return an array of bytes representing an integer.
        
          - length  
            Length of bytes object to use. An OverflowError is raised if the integer is not representable with the given number of bytes. Default is length 1.
        
          - byteorder  
            The byte order used to represent the integer. If byteorder is ‘big’, the most significant byte is at the beginning of the byte array. If byteorder is ‘little’, the most significant byte is at the end of the byte array. To request the native byte order of the host system, use [<span id="id2" class="problematic">\`</span>](#id1)sys.byteorder’ as the byte order value. Default is to use ‘big’.
        
          - signed  
            Determines whether two’s complement is used to represent the integer. If signed is False and a negative integer is given, an OverflowError is raised.
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.name "Link to this definition")  
        The name of the Enum member.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.value "Link to this definition")  
        The value of the Enum member.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_contains\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">other</span></span>*<span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__contains__ "Link to this definition")  
        Returns True if self has at least the same flags set as other.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_iter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__iter__ "Link to this definition")  
        Returns flags in definition order.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_len\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.ide.lsp.SemanticTokenModifiers.__len__ "Link to this definition")

</div>
