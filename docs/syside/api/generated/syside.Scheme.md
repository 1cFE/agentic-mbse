<div id="syside-scheme" class="section">

# syside.Scheme[](#syside-scheme "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Scheme</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.Scheme "Link to this definition")  
    Bases: `enum.Enum`
    
      - <span class="sig-name descname"><span class="pre">none</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.Scheme.none "Link to this definition")  
        Indicates that no scheme is present
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Unknown</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.Scheme.Unknown "Link to this definition")  
        Indicates the scheme is not a well-known scheme
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Ftp</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.Scheme.Ftp "Link to this definition")  
        File Transfer Protocol (FTP)
        
        FTP is a standard communication protocol used for the transfer of computer files from a server to a client on a computer network.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">File</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">3</span>*[](#syside.Scheme.File "Link to this definition")  
        File URI Scheme
        
        The File URI Scheme is typically used to retrieve files from within one’s own computer.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Http</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">4</span>*[](#syside.Scheme.Http "Link to this definition")  
        The Hypertext Transfer Protocol URI Scheme
        
        URLs of this type indicate a resource which is interacted with using the HTTP protocol.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Https</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">5</span>*[](#syside.Scheme.Https "Link to this definition")  
        The Secure Hypertext Transfer Protocol URI Scheme
        
        URLs of this type indicate a resource which is interacted with using the Secure HTTP protocol.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Ws</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">6</span>*[](#syside.Scheme.Ws "Link to this definition")  
        The WebSocket URI Scheme
        
        URLs of this type indicate a resource which is interacted with using the WebSocket protocol.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Wss</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">7</span>*[](#syside.Scheme.Wss "Link to this definition")  
        The Secure WebSocket URI Scheme
        
        URLs of this type indicate a resource which is interacted with using the Secure WebSocket protocol.
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.Scheme.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__dir__ "Link to this definition")  
        Returns public methods and other interesting attributes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.Scheme.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.Scheme.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.Scheme.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.name "Link to this definition")  
        The name of the Enum member.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Scheme.value "Link to this definition")  
        The value of the Enum member.

</div>
