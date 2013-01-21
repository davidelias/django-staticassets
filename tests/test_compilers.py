from staticassets import finder

from .test import TestCase


SASS_TEST = """
.content-navigation {
  border-color: #3bbfce;
  color: #2ca2af; }

.border {
  padding: 8px;
  margin: 8px;
  border-color: #3bbfce; }
""".strip('\n')

SCSS_TEST = """
.example .class-2, .example .class-3, .example .class-4 {
  background-color: #aaaaaa;
  border: 2px solid #777777;
  margin: 1em; }
.example .class-2 {
  margin-left: 1em; }
.example .class-3 {
  margin-left: 2em; }
.example .class-4 {
  margin-left: 3em; }
""".strip('\n')

STYLUS_TEST = """
body {
  font: 12px Helvetica, Arial, sans-serif;
}
a.button {
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
}
""".strip('\n')

LESS_TEST = """
#header {
  color: #4d926f;
}
h2 {
  color: #4d926f;
}
""".strip('\n')

COFFEESCRIPT_TEST = """
(function() {
  var square;

  if (typeof elvis !== "undefined" && elvis !== null) {
    alert("I knew it!");
  }

  square = function(x) {
    return x * x;
  };

}).call(this);
""".strip('\n')

EJS_TEST = """
function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='hello: '+
((__t=( name ))==null?'':__t)+
'\\n';
}
return __p;
}
""".strip('\n')

JST_TEST = """
(function() { this.JST || (this.JST = {}); this.JST['templates/list'] = <ul>
  <li>Item list</li>
</ul>
;}).call(this);
""".strip('\n')


class CompilersTest(TestCase):
    fixtures_dir = 'compilers'

    def test_compile_sass(self):
        self.assertEqual(SASS_TEST, finder.find('foo.sass').content.strip('\n'))

    def test_compile_scss_with_compass(self):
        self.assertEqual(SCSS_TEST, finder.find('compass.scss').content.strip('\n'))

    def test_compile_stylus(self):
        self.assertEqual(STYLUS_TEST, finder.find('stylus.styl').content.strip('\n'))

    def test_compile_less(self):
        self.assertEqual(LESS_TEST, finder.find('bar.less').content.strip('\n'))

    def test_compile_coffeescript(self):
        self.assertEqual(COFFEESCRIPT_TEST, finder.find('coffeescript.coffee').content.strip('\n'))

    def test_compile_ejs(self):
        self.assertEqual(EJS_TEST, finder.find('templates/detail.ejs').content.strip('\n'))

    def test_compile_jst(self):
        self.assertEqual(JST_TEST, finder.find('templates/list.jst').content.strip('\n'))
