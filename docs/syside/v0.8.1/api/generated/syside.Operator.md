<div id="syside-operator" class="section">

# syside.Operator[](#syside-operator "Link to this heading")

  - *<span class="pre">class</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">Operator</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span><span class="n"><span class="pre">args</span></span>*, *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwds</span></span>*<span class="sig-paren">)</span>[](#syside.Operator "Link to this definition")  
    Bases: `enum.Enum`
    
      - <span class="sig-name descname"><span class="pre">\_\_str\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.Operator.__str__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">If</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">0</span>*[](#syside.Operator.If "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">NullCoalescing</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">1</span>*[](#syside.Operator.NullCoalescing "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Implies</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">2</span>*[](#syside.Operator.Implies "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">LogicalOr</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">3</span>*[](#syside.Operator.LogicalOr "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Or</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">4</span>*[](#syside.Operator.Or "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Xor</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">5</span>*[](#syside.Operator.Xor "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">LogicalAnd</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">6</span>*[](#syside.Operator.LogicalAnd "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">And</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">7</span>*[](#syside.Operator.And "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Equals</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">8</span>*[](#syside.Operator.Equals "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Same</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">9</span>*[](#syside.Operator.Same "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">NotEquals</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">10</span>*[](#syside.Operator.NotEquals "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">NotSame</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">11</span>*[](#syside.Operator.NotSame "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">IsType</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">12</span>*[](#syside.Operator.IsType "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">HasType</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">13</span>*[](#syside.Operator.HasType "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">At</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">14</span>*[](#syside.Operator.At "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">AtAt</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">15</span>*[](#syside.Operator.AtAt "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">As</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">16</span>*[](#syside.Operator.As "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Meta</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">17</span>*[](#syside.Operator.Meta "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Less</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">18</span>*[](#syside.Operator.Less "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">LessEqual</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">19</span>*[](#syside.Operator.LessEqual "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Greater</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">20</span>*[](#syside.Operator.Greater "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">GreaterEqual</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">21</span>*[](#syside.Operator.GreaterEqual "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Range</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">22</span>*[](#syside.Operator.Range "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Plus</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">23</span>*[](#syside.Operator.Plus "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Minus</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">24</span>*[](#syside.Operator.Minus "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Multiply</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">25</span>*[](#syside.Operator.Multiply "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Divide</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">26</span>*[](#syside.Operator.Divide "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Modulo</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">27</span>*[](#syside.Operator.Modulo "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">ExponentStar</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">28</span>*[](#syside.Operator.ExponentStar "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">ExponentCaret</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">29</span>*[](#syside.Operator.ExponentCaret "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Conjugation</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">30</span>*[](#syside.Operator.Conjugation "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Not</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">31</span>*[](#syside.Operator.Not "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">All</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">32</span>*[](#syside.Operator.All "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Quantity</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">33</span>*[](#syside.Operator.Quantity "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Comma</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">34</span>*[](#syside.Operator.Comma "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">from\_string</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint">[<span class="pre">syside.Operator</span>](#syside.Operator "syside.Operator")</span></span>[](#syside.Operator.from_string "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Dot</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">36</span>*[](#syside.Operator.Dot "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Collect</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">37</span>*[](#syside.Operator.Collect "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Index</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">35</span>*[](#syside.Operator.Index "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Select</span></span>*<span class="w"> </span><span class="p"><span class="pre">=</span></span><span class="w"> </span><span class="pre">38</span>*[](#syside.Operator.Select "Link to this definition")
    
    <!-- end list -->
    
      - *<span class="pre">classmethod</span><span class="w"> </span>*<span class="sig-name descname"><span class="pre">\_\_signature\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.__signature__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_new\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">value</span></span>*<span class="sig-paren">)</span>[](#syside.Operator.__new__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_repr\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.__repr__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_dir\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.__dir__ "Link to this definition")  
        Returns public methods and other interesting attributes.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_format\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">format\_spec</span></span>*<span class="sig-paren">)</span>[](#syside.Operator.__format__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_hash\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.__hash__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_reduce\_ex\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">proto</span></span>*<span class="sig-paren">)</span>[](#syside.Operator.__reduce_ex__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_deepcopy\_\_</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">memo</span></span>*<span class="sig-paren">)</span>[](#syside.Operator.__deepcopy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">\_\_copy\_\_</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.__copy__ "Link to this definition")
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">name</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.name "Link to this definition")  
        The name of the Enum member.
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">value</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>[](#syside.Operator.value "Link to this definition")  
        The value of the Enum member.

</div>
