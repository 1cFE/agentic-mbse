<div id="package-contents" class="section">

<span id="syside-preview-api"></span>

# Package Contents[](#package-contents "Link to this heading")

<div class="admonition warning">

Warning

The features presented in this module are still in active development and may have breaking changes even with minor releases.

</div>

<div id="loading" class="section">

## Loading[](#loading "Link to this heading")

  - <span class="sig-name descname"><span class="pre">empty\_model</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings\_as\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Environment</span>](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.preview.LockedModel</span>](#syside.preview.LockedModel "syside.preview.LockedModel")</span></span>[](#syside.preview.empty_model "Link to this definition")  
    Opens an empty model, loading only standard library elements (unless `include_stdlib=False`).
    
    `unlock` the returned model before sharing between threads (and re-lock before use), or use a `with`-block to automatically unlock when exiting the block.
    
      - Parameters<span class="colon">:</span>
        
          - **warnings\_as\_errors** – if True, warnings are treated errors
        
          - **allow\_errors** – if True, tries to return a partial or invalid model even in the presence of errors
        
          - **include\_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library
        
          - **environment** – The environment to be used for the model. If this parameter is `None`, the default environment is used.
    
      - Returns<span class="colon">:</span>  
        a `LockableModel` representing an empty model.

<!-- end list -->

  - <span class="sig-name descname"><span class="pre">open\_model</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings\_as\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Environment</span>](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.preview.LockedModel</span>](#syside.preview.LockedModel "syside.preview.LockedModel")</span></span>[](#syside.preview.open_model "Link to this definition")  
    Opens a model stored in `paths`, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (`warnings_as_errors`) but is not allowed to contain errors (`allow_errors`).
    
    `unlock` the returned model before sharing between threads (and re-lock before use), or use a `with`-block to automatically unlock when exiting the block.
    
      - Parameters<span class="colon">:</span>
        
          - **paths** – path or sequence of paths (given as `str` or `Path`) of source files, or directories containing source files, to be included in the model
        
          - **warnings\_as\_errors** – if True, warnings are treated errors
        
          - **allow\_errors** – if True, tries to return a partial or invalid model even in the presence of errors
        
          - **include\_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library
        
          - **environment** – The environment to be used for the model. If this parameter is `None`, the default environment is used.
    
      - Returns<span class="colon">:</span>  
        a `LockableModel` representing the model loaded from source files given in `paths`
    
      - Raises<span class="colon">:</span>  
        [**syside.ModelError**](/v0.8.1/api/generated/syside.ModelError.md "syside.ModelError") – if model contains errors and `allow_errors` is False

<!-- end list -->

  - <span class="sig-name descname"><span class="pre">open\_model\_unlocked</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">paths</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span><span class="pre">pathlib.Path</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">warnings\_as\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">allow\_errors</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*, *<span class="n"><span class="pre">include\_stdlib</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">bool</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">True</span></span>*, *<span class="n"><span class="pre">environment</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Environment</span>](/v0.8.1/api/generated/syside.Environment.md "syside.Environment")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.preview.UnlockedModel</span>](#syside.preview.UnlockedModel "syside.preview.UnlockedModel")</span></span>[](#syside.preview.open_model_unlocked "Link to this definition")  
    Opens a model stored in `paths`, which can be given as a (combination of) file and directory paths. By default the model is allowed to generate warnings (`warnings_as_errors`) but is not allowed to contain errors (`allow_errors`).
    
    `lock` the returned model before access
    
      - Parameters<span class="colon">:</span>
        
          - **paths** – path or sequence of paths (given as `str` or `Path`) of source files, or directories containing source files, to be included in the model
        
          - **warnings\_as\_errors** – if True, warnings are treated errors
        
          - **allow\_errors** – if True, tries to return a partial or invalid model even in the presence of errors
        
          - **include\_stdlib** – if False, tries to load the model without also loading the SysML v2 standard library
        
          - **environment** – The environment to be used for the model. If this parameter is `None`, the default environment is used.
    
      - Returns<span class="colon">:</span>  
        an `UnlockedModel` representing the model loaded from source files given in `paths`
    
      - Raises<span class="colon">:</span>  
        [**syside.ModelError**](/v0.8.1/api/generated/syside.ModelError.md "syside.ModelError") – if model contains errors and `allow_errors` is False

<!-- end list -->

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">LockedModel</span></span>[](#syside.preview.LockedModel "Link to this definition")  
    A SysML v2/KerML model interface. Top level elements (typically Packages) can be accessed through the `lookup` method, e.g. `model.lookup("PackageName")`. To create a new top level package use the `new_top_level_package` method.
    
    The object is invalidated once `unlock`ed, either explicitly or by leaving the outermost `with`-block when used as a context manager.
    
    Note that `LockedModel` is generally not intended to be instantiated directly. Ideally, use either `open_model` or `empty_model`. Alternatively, instantiate `UnlockedModel` and use `UnlockedModel.lock`.
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        model : LockedModel = empty_model()
        
        ## Alternatively
        unlocked_model = open_model_unlocked(...)
        
        model : LockedModel = unlocked_model.lock()
    
    </div>
    
    </div>
    
    Initialization
    
      - <span class="sig-name descname"><span class="pre">\_\_enter\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Self</span></span></span>[](#syside.preview.LockedModel.__enter__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_exit\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">exc\_type</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">type</span><span class="p"><span class="pre">\[</span></span><span class="pre">BaseException</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">exc\_value</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">BaseException</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*, *<span class="n"><span class="pre">traceback</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">types.TracebackType</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">bool</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.preview.LockedModel.__exit__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">unlock</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.preview.UnlockedModel</span>](#syside.preview.UnlockedModel "syside.preview.UnlockedModel")</span></span>[](#syside.preview.LockedModel.unlock "Link to this definition")  
        Unlocks the model, freeing it up for others to lock.
        
          - Returns<span class="colon">:</span>  
            `UnlockedModel` that can be used to re-acquire access to the model
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - *<span class="pre">property</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">diagnostics</span></span>*<span class="p"><span class="pre">:</span></span><span class="w"> </span>[<span class="pre">syside.Diagnostics</span>](/v0.8.1/api/generated/syside.Diagnostics.md "syside.Diagnostics")*[](#syside.preview.LockedModel.diagnostics "Link to this definition")  
        Diagnostics generated when the model was loaded.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">top\_elements</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.preview.LockedModel.top_elements "Link to this definition")  
        Yields all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account.
        
          - Returns<span class="colon">:</span>  
            sequence of top level elements
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">top\_named\_elements</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">tuple</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">,</span></span><span class="w"> </span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.preview.LockedModel.top_named_elements "Link to this definition")  
        Yields all named top level named elements (typically Packages) that are owned members of a root namespace in the model, together with (one of) their names. Note that imported members are not taken into account.
        
        Prefers name over short name.
        
          - Returns<span class="colon">:</span>  
            sequence of (name, element) pairs of named top level elements
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">top\_names</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span></span>[](#syside.preview.LockedModel.top_names "Link to this definition")  
        Yields names of all top level named elements (typically Packages) that are owned members of a root namespace in the model. Note that imported members are not taken into account.
        
        Prefers name over short name.
        
          - Returns<span class="colon">:</span>  
            sequence of names of named top level elements
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">lookup</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*, *<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">None</span></span></span>[](#syside.preview.LockedModel.lookup "Link to this definition")  
        If `path` is empty, yields the (unique) top-level owned member element with name `name` if it exists, otherwise returns `None`. Note that elements other than owned member elements, such as imported or inherited ones, are not taken into account.
        
        Otherwise `.lookup(name, name, path1, ..., pathn)` is equal to `.lookup(name).lookup(path1).[...].lookup(pathn)`, unless any intermediate value is `None`. If any intermediate value is `None` the whole expression evaluates to `None`.
        
          - Parameters<span class="colon">:</span>
            
              - **name** – name of element to find
            
              - **path** – sequence of names to (recursively) lookup
        
          - Returns<span class="colon">:</span>  
            (unique) element with name `name` or None (if not found)
        
          - Raises<span class="colon">:</span>
            
              - **RuntimeError** – if used after unlocking
            
              - **TypeError** – if trying to recursively look-up into a non-`Namespace` element.
            
              - **NameError** – if the name is ambiguous.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">top\_elements\_from</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span><span class="pre">pathlib.Path</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">Iterator</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Element</span>](/v0.8.1/api/metamodel/KerML/Element.md "syside.Element")<span class="p"><span class="pre">\]</span></span></span></span>[](#syside.preview.LockedModel.top_elements_from "Link to this definition")  
        Yields top level owned member elements (typically Packages) loaded from the specified path(or from files below that path if it is a directory). Note that imported members are not taken into account.
        
          - Parameters<span class="colon">:</span>  
            **path** – source file or directory path to return elements loaded from
        
          - Returns<span class="colon">:</span>  
            sequence of (top) model elements loaded from source file(s) matching `path`
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">new\_top\_level\_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Package</span>](/v0.8.1/api/metamodel/KerML/Package.md "syside.Package")</span></span>[](#syside.preview.LockedModel.new_top_level_package "Link to this definition")  
        Creates a (named) new top level package.
        
          - Parameters<span class="colon">:</span>  
            **name** – name of the new package
        
          - Returns<span class="colon">:</span>  
            a new `syside.Package` named `name` (in a new global namespace)
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">new\_top\_level\_library\_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">str</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.LibraryPackage</span>](/v0.8.1/api/metamodel/KerML/LibraryPackage.md "syside.LibraryPackage")</span></span>[](#syside.preview.LockedModel.new_top_level_library_package "Link to this definition")  
        Creates a (named) new top level package.
        
          - Parameters<span class="colon">:</span>  
            **name** – name of the new package
        
          - Returns<span class="colon">:</span>  
            a new `syside.LibraryPackage` named `name` (in a new global namespace)
        
          - Raises<span class="colon">:</span>  
            **RuntimeError** – if used after unlocking

<!-- end list -->

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">UnlockedModel</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">documents</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Iterable</span><span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.SharedMutex</span>](/v0.8.1/api/generated/syside.SharedMutex.md "syside.SharedMutex")<span class="p"><span class="pre">\[</span></span>[<span class="pre">syside.Document</span>](/v0.8.1/api/generated/syside.Document.md "syside.Document")<span class="p"><span class="pre">\]</span></span><span class="p"><span class="pre">\]</span></span></span>*, *<span class="n"><span class="pre">diagnostics</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Diagnostics</span>](/v0.8.1/api/generated/syside.Diagnostics.md "syside.Diagnostics")</span>*<span class="sig-paren">)</span>[](#syside.preview.UnlockedModel "Link to this definition")  
    A SysML v2/KerML model that needs to be `lock`ed before access.
    
    Note that `UnlockedModel` is generally not intended to be instantiated directly. Ideally, use `open_model_unlocked` or `LockedModel.unlock` on a previously acquired `LockedModel`.
    
    <div class="highlight-python notranslate">
    
    <div class="highlight">
    
        model : UnlockedModel = open_model_unlocked("file.sysml")
        
        ## Alternatively
        locked_model : LockedModel = open_model("file.sysml")
        ...
        model = locked_model.unlock()
    
    </div>
    
    </div>
    
    Initialization
    
      - Parameters<span class="colon">:</span>
        
          - **documents** – sequence of `syside.Document`s that constitute the model
        
          - **diagnostics** – any diagnostic messages (errors or warnings) concerning the model
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">lock</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.preview.LockedModel</span>](#syside.preview.LockedModel "syside.preview.LockedModel")</span></span>[](#syside.preview.UnlockedModel.lock "Link to this definition")  
        Locks the model, allowing access.
        
          - Returns<span class="colon">:</span>  
            a `LockedModel` that allows access to model elements.

</div>

<div id="building" class="section">

## Building[](#building "Link to this heading")

  - <span class="sig-name descname"><span class="pre">new\_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">owner</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Namespace</span>](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace")</span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">short\_name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">visibility</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">Literal</span><span class="p"><span class="pre">\[</span></span><span class="pre">private</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">protected</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">public</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.VisibilityKind</span>](/v0.8.1/api/metamodel/KerML/VisibilityKind.md "syside.VisibilityKind")<span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Package</span>](/v0.8.1/api/metamodel/KerML/Package.md "syside.Package")</span></span>[](#syside.preview.new_package "Link to this definition")  
    Adds a new package (Section 7.5)

<!-- end list -->

  - <span class="sig-name descname"><span class="pre">new\_library\_package</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">owner</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Namespace</span>](/v0.8.1/api/metamodel/KerML/Namespace.md "syside.Namespace")</span>*, *<span class="n"><span class="pre">name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">short\_name</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">str</span><span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">visibility</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">Literal</span><span class="p"><span class="pre">\[</span></span><span class="pre">private</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">protected</span><span class="p"><span class="pre">,</span></span><span class="w"> </span><span class="pre">public</span><span class="p"><span class="pre">\]</span></span><span class="w"> </span><span class="p"><span class="pre">|</span></span><span class="w"> </span>[<span class="pre">syside.VisibilityKind</span>](/v0.8.1/api/metamodel/KerML/VisibilityKind.md "syside.VisibilityKind")<span class="p"><span class="pre">\]</span></span></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.LibraryPackage</span>](/v0.8.1/api/metamodel/KerML/LibraryPackage.md "syside.LibraryPackage")</span></span>[](#syside.preview.new_library_package "Link to this definition")  
    Adds a new package (Section 7.5)

</div>

</div>
