<div id="syside-formatoptions" class="section">

# syside.FormatOptions[](#syside-formatoptions "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">FormatOptions</span></span>[](#syside.FormatOptions "Link to this definition")  
    Initialization
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">null\_expression</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.NullFormat</span>](/v0.8.1/api/generated/syside.NullFormat.md "syside.NullFormat")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.null_expression "Link to this definition")  
        Controls `NullExpression` formatting:
        
          - `null`: always formatted as `null`
        
          - `brackets`: always formatted as `()`
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">literal\_real</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FloatFormat</span>](/v0.8.1/api/generated/syside.FloatFormat.md "syside.FloatFormat")*[](#syside.FormatOptions.literal_real "Link to this definition")  
        Controls `LiteralReal` formatting. Only applies to those numbers that are not in the source text.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">strip\_unnecessary\_quotes</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.strip_unnecessary_quotes "Link to this definition")  
        Controls identifier formatting. If true, strips quotes from identifiers if the name doesn’t have restricted characters
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">sequence\_expression\_trailing\_comma</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.sequence_expression_trailing_comma "Link to this definition")  
        Controls `SequenceExpression` trailing comma formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">operator\_break</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OperatorBreak</span>](/v0.8.1/api/generated/syside.OperatorBreak.md "syside.OperatorBreak")*[](#syside.FormatOptions.operator_break "Link to this definition")  
        Controls binary operator placement on line breaks.
        
          - `after`: operators are placed on the same line as the LHS expression
        
          - `before`: operators are placed on the same line as the RHS expression
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">comment\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.comment_keyword "Link to this definition")  
        Controls `comment` keyword formatting:
        
          - `always`: `comment` will always be printed
        
          - `as-needed`: `comment` will only be printed as needed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">comment\_about\_break</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")*[](#syside.FormatOptions.comment_about_break "Link to this definition")  
        Controls line break preceding `about` in `Comment`:
        
          - `always`: about list is always on a new line
        
          - `as-needed`: printer tries to fit about list on the previous line
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">markdown\_comments</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.markdown_comments "Link to this definition")  
        Controls `Comment` and `Documentation` body formatting. If true, trailing whitespace is preserved on each line but last.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">textual\_representation\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.textual_representation_keyword "Link to this definition")  
        Controls `rep` keyword formatting:
        
          - `always`: `rep` will always be printed
        
          - `as-needed`: `rep` will only be printed as needed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">textual\_representation\_language\_break</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")*[](#syside.FormatOptions.textual_representation_language_break "Link to this definition")  
        Controls line break preceding `language` in `TextualRepresentation`:
        
          - `always`: language is always on a new line
        
          - `as-needed`: printer tries to fit language on the previous line
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">empty\_namespace\_brackets</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.empty_namespace_brackets "Link to this definition")  
        Controls formatting of empty children blocks:
        
          - `always`: empty blocks are always formatted as `{}`
        
          - `never`: empty blocks are always formatted as a trailing `;`
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_declaration\_disjoining</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_declaration_disjoining "Link to this definition")  
        Controls disjoining formatting in type declarations. If true, all disjoinings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_unioning</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_unioning "Link to this definition")  
        Controls unioning formatting in type declarations. If true, all unionings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_intersecting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_intersecting "Link to this definition")  
        Controls intersecting formatting in type declarations. If true, all intersectings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_differencing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_differencing "Link to this definition")  
        Controls differencing formatting in type declarations. If true, all differencings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_feature\_chaining</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_feature_chaining "Link to this definition")  
        Controls feature chaining formatting in feature declarations. If true, all feature chainings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">merge\_declaration\_type\_featuring</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.merge_declaration_type_featuring "Link to this definition")  
        Controls type featuring formatting in feature declarations. If true, all type featurings are merged into a single group. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_specialization</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_specialization "Link to this definition")  
        Controls specialization formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_conjugation</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_conjugation "Link to this definition")  
        Controls conjugation formatting. Requires KerML.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_subsetting "Link to this definition")  
        Controls subsetting formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_subclassification</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_subclassification "Link to this definition")  
        Controls subclassification formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_redefinition</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_redefinition "Link to this definition")  
        Controls redefinition formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_reference\_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_reference_subsetting "Link to this definition")  
        Controls reference subsetting formatting in feature declarations.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_cross\_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_cross_subsetting "Link to this definition")  
        Controls cross subsetting formatting in feature declarations.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_feature\_typing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_feature_typing "Link to this definition")  
        Controls feature typing formatting.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">declaration\_conjugated\_port\_typing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.declaration_conjugated_port_typing "Link to this definition")  
        Controls conjugated port typing formatting in port declarations.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature\_value\_equals</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.feature_value_equals "Link to this definition")  
        Controls feature value equals token formatting whenever it can be omitted:
        
          - `as-needed`: `=` will only be printed if it is required by the grammar
        
          - `always`: `=` will be always printed when it is acceptable by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">feature\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.feature_keyword "Link to this definition")  
        Controls `feature` keyword formatting in KerML:
        
          - `always`: `feature` keyword is always printed
        
          - `as-needed`: `feature` keyword is printed only when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">public\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.public_keyword "Link to this definition")  
        Controls `public` keyword formatting:
        
          - `always`: `public` will always be printed
        
          - `never`: `public` will never be printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">specialization\_keyword\_specialization</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.specialization_keyword_specialization "Link to this definition")  
        Controls `specialization` keyword formatting in specialization members:
        
          - `always`: `specialization` will always be printed.
        
          - `as-needed`: `specialization` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">specialization\_keyword\_subclassification</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.specialization_keyword_subclassification "Link to this definition")  
        Controls `specialization` keyword formatting in subclassification members:
        
          - `always`: `specialization` will always be printed.
        
          - `as-needed`: `specialization` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">specialization\_keyword\_feature\_typing</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.specialization_keyword_feature_typing "Link to this definition")  
        Controls `specialization` keyword formatting in feature typing members:
        
          - `always`: `specialization` will always be printed.
        
          - `as-needed`: `specialization` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">specialization\_keyword\_subsetting</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.specialization_keyword_subsetting "Link to this definition")  
        Controls `specialization` keyword formatting in subsetting members:
        
          - `always`: `specialization` will always be printed.
        
          - `as-needed`: `specialization` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">specialization\_keyword\_redefinition</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.specialization_keyword_redefinition "Link to this definition")  
        Controls `specialization` keyword formatting in redefinition members:
        
          - `always`: `specialization` will always be printed.
        
          - `as-needed`: `specialization` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">conjugation\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.conjugation_keyword "Link to this definition")  
        Controls `conjugation` keyword formatting in conjugation members:
        
          - `always`: `conjugation` will always be printed.
        
          - `as-needed`: `conjugation` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">disjoining\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.disjoining_keyword "Link to this definition")  
        Controls `disjoining` keyword formatting in disjoining members:
        
          - `always`: `disjoining` will always be printed.
        
          - `as-needed`: `disjoining` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">inverting\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.inverting_keyword "Link to this definition")  
        Controls `inverting` keyword formatting in inverting members:
        
          - `always`: `inverting` will always be printed.
        
          - `as-needed`: `inverting` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">featuring\_of\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.featuring_of_keyword "Link to this definition")  
        Controls `of` keyword formatting in type featuring members:
        
          - `always`: `of` will always be printed.
        
          - `as-needed`: `of` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">dependency\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.dependency_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in dependencies:
        
          - `always`: `from` will always be printed.
        
          - `as-needed`: `from` will be printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">invariant\_true\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.invariant_true_keyword "Link to this definition")  
        Controls `true` keyword formatting in invariants:
        
          - `never`: `true` is never printed
        
          - `always`: `true` is always printed if invariant is not negated
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">multiplicity\_placement</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.MultiPlacement</span>](/v0.8.1/api/generated/syside.MultiPlacement.md "syside.MultiPlacement")*[](#syside.FormatOptions.multiplicity_placement "Link to this definition")  
        Controls multiplicity placement in type declarations:
        
          - `first`: multiplicity is printed before any specializations
        
          - `first-specialization`: multiplicity is printed after the first specialization
        
          - `last`: multiplicity is printed after all specializations
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata\_feature\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.KwToken</span>](/v0.8.1/api/generated/syside.KwToken.md "syside.KwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.metadata_feature_keyword "Link to this definition")  
        Controls metadata feature keyword used.
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata\_body\_feature\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.metadata_body_feature_keyword "Link to this definition")  
        Controls `feature` (KerML) and `ref` (SysML) keyword formatting in metadata features:
        
          - `always`: keywords are always printed
        
          - `never`: keywords are never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">metadata\_body\_feature\_redefines</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKwToken</span>](/v0.8.1/api/generated/syside.OptionalKwToken.md "syside.OptionalKwToken")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.metadata_body_feature_redefines "Link to this definition")  
        Controls first feature redefinition formatting inside MetadataFeature bodies:
        
          - `keyword`: `redefines` is printed
        
          - `token`: `:>>` is printed
        
          - `none`: nothing is printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_allocation\_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_allocation_usages "Link to this definition")  
        Controls allocation usage ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_connectors</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_connectors "Link to this definition")  
        Controls connector ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_connectors\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_connectors_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in binary connectors:
        
          - `always`: `from` is always printed
        
          - `as-needed`: `from` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_binding\_connectors</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_binding_connectors "Link to this definition")  
        Controls binding connector ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_binding\_connector\_of\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_binding_connector_of_keyword "Link to this definition")  
        Controls `of` keyword formatting in binary binding connectors:
        
          - `always`: `of` is always printed
        
          - `as-needed`: `of` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_successions</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_successions "Link to this definition")  
        Controls succession ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_succession\_first\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_succession_first_keyword "Link to this definition")  
        Controls `first` keyword formatting in binary successions:
        
          - `always`: `first` is always printed
        
          - `as-needed`: `first` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">flow\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.flow_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in flows:
        
          - `always`: `from` is always printed
        
          - `as-needed`: `from` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">succession\_flow\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.succession_flow_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in succession flows:
        
          - `always`: `from` is always printed
        
          - `as-needed`: `from` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">flow\_usage\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.flow_usage_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in flow usages:
        
          - `always`: `from` is always printed
        
          - `as-needed`: `from` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">succession\_flow\_usage\_from\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.succession_flow_usage_from_keyword "Link to this definition")  
        Controls `from` keyword formatting in succession flow usages:
        
          - `always`: `from` is always printed
        
          - `as-needed`: `from` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">ordered\_nonunique\_priority</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.MultiOrder</span>](/v0.8.1/api/generated/syside.MultiOrder.md "syside.MultiOrder")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.ordered_nonunique_priority "Link to this definition")  
        Controls `ordered` and `nonunique` print order:
        
          - `ordered`: `ordered` is printed first
        
          - `nonunique`: `nonunique` is printed first
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">enum\_member\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.enum_member_keyword "Link to this definition")  
        Controls `enum` keyword formatting inside enum definitions:
        
          - `always`: `enum` is always printed
        
          - `never`: `enum` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">occurrence\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.occurrence_keyword "Link to this definition")  
        Controls `occurrence` keyword formatting in occurrence usages and definitions:
        
          - `always`: `occurrence` is always printed
        
          - `as-needed`: `occurrence` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binding\_connector\_as\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binding_connector_as_usage_keyword "Link to this definition")  
        Controls `binding` formatting in binding connectors as usages:
        
          - `always`: `binding` is always printed
        
          - `as-needed`: `binding` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">succession\_as\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.succession_as_usage_keyword "Link to this definition")  
        Controls `succession` formatting in successions as usages:
        
          - `always`: `succession` is always printed
        
          - `as-needed`: `succession` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">assert\_constraint\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.assert_constraint_usage_keyword "Link to this definition")  
        Controls `constraint` formatting in assert constraint usages:
        
          - `always`: `constraint` is always printed
        
          - `as-needed`: `constraint` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">event\_occurrence\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.event_occurrence_keyword "Link to this definition")  
        Controls `occurrence` keyword formatting in event occurrence usages:
        
          - `always`: `occurrence` is always printed
        
          - `as-needed`: `occurrence` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">exhibit\_state\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.exhibit_state_usage_keyword "Link to this definition")  
        Controls `state` formatting in exhibit state usages:
        
          - `always`: `state` is always printed
        
          - `as-needed`: `state` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_use\_case\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.include_use_case_usage_keyword "Link to this definition")  
        Controls `use case` formatting in include use case usages:
        
          - `always`: `use case` is always printed
        
          - `as-needed`: `use case` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">perform\_action\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.perform_action_usage_keyword "Link to this definition")  
        Controls `action` formatting in perform action usages:
        
          - `always`: `action` is always printed
        
          - `as-needed`: `action` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">satisfy\_requirement\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.satisfy_requirement_keyword "Link to this definition")  
        Controls `requirement` formatting in satisfy requirement usages:
        
          - `always`: `requirement` is always printed
        
          - `as-needed`: `requirement` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">satisfy\_requirement\_assert\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.satisfy_requirement_assert_keyword "Link to this definition")  
        Controls `assert` formatting in satisfy requirement usages:
        
          - `always`: `assert` is always printed
        
          - `never`: `assert` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">allocation\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.allocation_usage_keyword "Link to this definition")  
        Controls `allocation` formatting in allocation usages:
        
          - `always`: `allocation` is always printed
        
          - `as-needed`: `allocation` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">connection\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.connection_usage_keyword "Link to this definition")  
        Controls `connection` formatting in connection usages:
        
          - `always`: `connection` is always printed
        
          - `as-needed`: `connection` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_connection\_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_connection_usages "Link to this definition")  
        Controls connection usage ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">binary\_interface\_usages</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.binary_interface_usages "Link to this definition")  
        Controls interface usage ends formatting:
        
          - `always`: binary ends are printed as binary declaration
        
          - `never`: binary ends are printed as nary declaration
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">interface\_usage\_connect\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.interface_usage_connect_keyword "Link to this definition")  
        Controls `connect` formatting in interface usages:
        
          - `always`: `connect` is always printed
        
          - `as-needed`: `connect` is only printed when required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">action\_node\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.action_node_keyword "Link to this definition")  
        Controls `action` formatting in action nodes:
        
          - `always`: `action` is always printed
        
          - `as-needed`: `action` is printed only if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">while\_loop\_parenthesize\_condition</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.while_loop_parenthesize_condition "Link to this definition")  
        Controls `while (...)` while loop action condition expression formatting:
        
          - `always`: expression is printed with parentheses
        
          - `never`: expression is printed without parentheses
        
          - `on-break`: expression is printed with parentheses only if it breaks
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">while\_loop\_parenthesize\_until</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.while_loop_parenthesize_until "Link to this definition")  
        Controls `until (...)` while loop action condition expression formatting:
        
          - `always`: expression is printed with parentheses
        
          - `never`: expression is printed without parentheses
        
          - `on-break`: expression is printed with parentheses only if it breaks
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">if\_parenthesize\_condition</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.if_parenthesize_condition "Link to this definition")  
        Controls `if (...)` condition expression formatting:
        
          - `always`: expression is printed with parentheses
        
          - `never`: expression is printed without parentheses
        
          - `on-break`: expression is printed with parentheses only if it breaks
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">transition\_usage\_parenthesize\_guard</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.transition_usage_parenthesize_guard "Link to this definition")  
        Controls `if (...)` condition expression in transition usages formatting:
        
          - `always`: expression is printed with parentheses
        
          - `never`: expression is printed without parentheses
        
          - `on-break`: expression is printed with parentheses only if it breaks
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">element\_filter\_parenthesize</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.OptionalToken</span>](/v0.8.1/api/generated/syside.OptionalToken.md "syside.OptionalToken")*[](#syside.FormatOptions.element_filter_parenthesize "Link to this definition")  
        Controls `filter (...)` condition expression in element filter memberships formatting:
        
          - `always`: expression is printed with parentheses
        
          - `never`: expression is printed without parentheses
        
          - `on-break`: expression is printed with parentheses only if it breaks
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">transition\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.transition_usage_keyword "Link to this definition")  
        Controls `transition` formatting in transition usages:
        
          - `always`: `transition` is always printed if permitted by the grammar
        
          - `as-needed`: `transition` is only printed if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">transition\_usage\_first\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.transition_usage_first_keyword "Link to this definition")  
        Controls `first` formatting in transition usages:
        
          - `always`: `first` is always printed if permitted by the grammar
        
          - `as-needed`: `first` is only printed if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">framed\_concern\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.framed_concern_keyword "Link to this definition")  
        Controls `concern` formatting in framed concern usages:
        
          - `always`: `concern` is always printed
        
          - `as-needed`: `concern` is only printed if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">reference\_usage\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.OptionalKw</span>](/v0.8.1/api/generated/syside.OptionalKw.md "syside.OptionalKw")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.reference_usage_keyword "Link to this definition")  
        Controls `ref` formatting in reference usages:
        
          - `always`: `ref` is always printed
        
          - `as-needed`: `ref` is only printed if required by the grammar
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">attribute\_usage\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.attribute_usage_reference_keyword "Link to this definition")  
        Controls `ref` formatting in attribute usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">event\_occurrence\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.event_occurrence_reference_keyword "Link to this definition")  
        Controls `ref` formatting in event occurrence usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">port\_usage\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.port_usage_reference_keyword "Link to this definition")  
        Controls `ref` formatting in attribute usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">connection\_usage\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.connection_usage_reference_keyword "Link to this definition")  
        Controls `ref` formatting in connection usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">connector\_as\_usage\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.connector_as_usage_reference_keyword "Link to this definition")  
        Controls `ref` formatting in connector as usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">exhibit\_state\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.exhibit_state_reference_keyword "Link to this definition")  
        Controls `ref` formatting in exhibit state usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">include\_use\_case\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.include_use_case_reference_keyword "Link to this definition")  
        Controls `ref` formatting in include use case usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">perform\_action\_reference\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.perform_action_reference_keyword "Link to this definition")  
        Controls `ref` formatting in perform action usages:
        
          - `always`: `ref` is always printed
        
          - `never`: `ref` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">interface\_port\_keyword</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.FormatPreserved</span>](/v0.8.1/api/generated/syside.FormatPreserved.md "syside.FormatPreserved")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.AlwaysNever</span>](/v0.8.1/api/generated/syside.AlwaysNever.md "syside.AlwaysNever")<span class="p"><span class="pre">\]</span></span>*[](#syside.FormatOptions.interface_port_keyword "Link to this definition")  
        Controls `port` formatting of default interface ends:
        
          - `always`: `port` is always printed
        
          - `never`: `port` is never printed
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">force\_break\_bodies</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">bool</span>*[](#syside.FormatOptions.force_break_bodies "Link to this definition")  
        If true, any child elements inside bodies will be printed on new line.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_cpp\_name\_\_</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">'syside::sysml::FormatOptions'</span>*[](#syside.FormatOptions.__cpp_name__ "Link to this definition")

</div>
