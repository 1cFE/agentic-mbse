<div id="syside-encodingopts" class="section">

# syside.EncodingOpts[](#syside-encodingopts "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">EncodingOpts</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">space\_as\_plus</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">lower\_case</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">disallow\_null</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span>[](#syside.EncodingOpts "Link to this definition")  
    Percent-encoding options
    
    These options are used to customize the behavior of algorithms which use percent escapes, such as encoding or decoding.
    
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">space\_as\_plus</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.EncodingOpts.space_as_plus "Link to this definition")  
        True if spaces encode to and from plus signs
        
        This option controls whether or not the PLUS character (“+”) is used to represent the SP character (” “) when encoding or decoding. Although not prescribed by the RFC, plus signs are commonly treated as spaces upon decoding when used in the query of URLs using well known schemes such as HTTP.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">lower\_case</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.EncodingOpts.lower_case "Link to this definition")  
        True if hexadecimal digits are emitted as lower case
        
        By default, percent-encoding algorithms emit hexadecimal digits A through F as uppercase letters. When this option is `true`, lowercase letters are used.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">disallow\_null</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.EncodingOpts.disallow_null "Link to this definition")  
        True if nulls are not allowed
        
        Normally all possible character values (from 0 to 255) are allowed, with reserved characters being replaced with escapes upon encoding. When this option is true, attempting to decode a null will result in an error.

</div>
