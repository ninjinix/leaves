#!/usr/bin/ruby
require 'cgi'
require 'fileutils'
#================================================================
def icgi
  $cgi ||= CGI.new
end

def cgip(s)
  icgi.params[s.to_s].first
end

def esc(s)
  s ? CGI.escapeHTML(s) : nil
end

def unesc(s)
  s ? CGI.unescapeHTML(s) : nil
end

def contentText(s)
  "Content-type: text/plean; charset=utf-8\n\n"+s
end

def contentJson(s)
  "Content-Type: application/json; charset=utf-8\n\n"+s
end

def s2json(s)
  '"'+s.gsub(/\r/,'\r').gsub(/\n/,'\n').gsub(/"/,'\"')+'"'
end

SCRIPT_NAME = File.basename(icgi.script_name)

#================================================================
SITE_NAME = 'Masonry Cloud'

CSS = <<EOD
<!--
html {-webkit-text-size-adjust:none;}
* {line-height: 120%; font-size: 100%;
  font-family: Consolas, 'Courier New', Courier, Monaco, monospace;}
body {margin: 0; padding: 0; background: #000 url(bg002.jpg) fixed;
  font-size: 12px; color: #ddd;}
a {color: #8ac; text-decoration: none;}
p {padding: 0; margin: 1em 0;}
h1 {font-weight: normal; margin: 0 0 0.5em 0; padding: 0;
  border-bottom: dashed 1px #8ac; color: #8ac;}
h2 {font-weight: normal; margin: 1em 0 0.5em 0; padding: 0;
  border-bottom: dashed 1px #8ac; color: #8ac;}
table {margin: 0em; border-collapse: collapse;}
td {padding: 3px 6px; border: 1px solid #567;}

#header {
  background: rgba(255,255,255,0.75);
  margin-bottom: 5px;
  padding: 12px;
  color: #445;
}
#header input {padding: 0; margin: 0;
  background: #fff; color: #444; border: 1px solid #aac;}

.masonry {margin: 0 auto;}
.item {border-radius: 5px; background-color: rgba(255,255,255,0.75);
  margin: 5px; padding: 5px; width: 460px; color: #678;}

.item.main {background-color: rgba(255,255,255,0.85);}
.item.sub  {background-color: rgba(255,255,255,0.75);}
.item.sub h1 {color: #8ac; border-color: #8ac;}

#txt {width: 98%; height: 25em; margin-bottom: 3px;
  background: rgba(0,0,0,0);
  border: 1px solid #aaa; color: #444;}
#write {padding: 0 10px; margin: 0 5px 0 0;}
#close {padding: 0 10px; margin: 0 5px 0 0;}

-->
EOD

# <div class="item">
# <h1>Main</h1>
# <textarea id="txt"></textarea><br/>
# <input type="submit" id="write" value="write" onClick="writeItem()"/>
# </div>

SCRIPT = <<EOD
<!--
var container = 0;
var masonry = 0;

function ajaxPost(d, f) {
  $.ajax({
    type: "POST", scriptCharset: 'utf-8', dataType: "json", cache: false,
    url: "#{SCRIPT_NAME}", data: d, success: f,
    error: function(xhr, textStatus, errorThrown) { alert(textStatus); }
  });
}
function removeItem(v) {
  masonry.remove(v);
}
function prependItem(v) {
  container.insertBefore(v, container.firstChild);
  masonry.prepended(v);
}

function touchItem(s, isEdit) {
  removeItem($('#'+s)[0]);
  removeItem($('.item.main')[0]);
  ajaxPost({touch:s}, function(data, dataType) {
    var m = $(data.main);
    if (isEdit) {
      m.find(".view").hide();
      m.find(".write").show();
    }
    prependItem($(data.sub)[0]);
    prependItem(m[0]);
  });
}
function mainEdit() {
  $(".view").toggle(200);
  $(".write").toggle(200, function() {
    masonry.layout();
  });
  return false;
}
function subEdit(s) {
  touchItem(s, true);
}









$(function(){
  $("#word").keypress(function(e) {
    if (e.which == 13) {
      $("#word").val("");
    }
  });
  shortcut.add("e",function() {
    mainEdit();
  },{
    'disable_in_input':true
  });
  container = $(".masonry")[0];
  masonry = new Masonry(container, {
    itemSelector: '.item',
    columnWidth: 0,
    isFitWidth: true
  });
}); 

//-->
EOD

def files
  $files ||= Dir["d/*"].sort_by{|a|-File.stat(a).mtime.to_i}.
    map{|i| CGI.unescape(File.basename(i))}
end

def link_self(s,c='nop')
  %|<a class="#{c}" href="#{SCRIPT_NAME}#{
    s == 'FrontPage' ? nil : '?' + esc(CGI.escape(s))}">#{esc(s)}</a>|
end

def s2view(s)
  w = files.map{|i| Regexp.escape(i)}.join('|')
  esc(s+"\n").gsub(/((^,.+\n)+|\n)/){
    case $1
    when /((^,.+\n)+)/
      "<table>\n" + $1.split("\n").map{|i|
        "<tr>" + i.split(',').map{|i|
          i=='' ? '' : "<td>#{i}</td>"}.join + "</tr>\n"
      }.join + "</table>\n"
    when "\n" then "<br/>\n"
    end
  }.gsub(/( |\t|\[\[.+?\]\]|(http:|https:)\/\/[^\s<>]+|(#{w}))/){
    case $1
    when " "
      then '&nbsp;'
    when "\t"
      then '&nbsp;&nbsp;&nbsp;&nbsp;'
    when %r!\[\[rest:(\d+)/(\d+)/(\d+)\]\]!
      then ((Time.local($1,$2,$3) - Time.now) / (60*60*24)).ceil
    when /\[\[((?:http:|https:)\S+?)\s+?(.+?)\]\]/
      then %|<a href="#{$1}" target="_blank">#{$2}</a>|
    when /\[\[(\S+?)\]\]/
      then %|<a href="?#{CGI.escape(unesc($1))}">#{$1}</a>|
    when /((http:|https:)\/\/[^\s<>]+)/
      then %|<a href="#{$1}" target="_blank">#{$1}</a>|
    when /(#{w})/
      then link_self($1,'auto')
    else '?'
    end
  }
end

def xmain(t)
  return "" unless t
  s = CGI.escape(t)
  return <<EOD unless test('f', "d/"+s)
dododo
EOD
  txt = open("d/"+s){|f|f.read}
  <<EOD
<div id="#{s}" class="item main">
<div style="float:right;">
  <a href="#" onclick="mainEdit()">[Edit]</a>
</div>
<h1 class="word">#{t}</h1>

<div class="write" style="display: none">
<textarea id="txt">
#{txt}
</textarea>
<input type="submit" id="write" value="Write"/>\
<input type="submit" id="close" value="Close" onclick="mainEdit()"/>
</div>

<div class="view">
#{s2view txt}
<h2>Link</h2> 検索結果的なの
</div>

</div>
EOD
end

def xsub(t)
  return "" unless t
  s = CGI.escape(t)
  return "" unless test('f', "d/"+s)
  txt = open("d/"+s){|f|f.read}
  <<EOD
<div id="#{s}" class="item sub">
<div style="float:right;">
  <a href="#" onclick="subEdit('#{s}')">[Edit]</a>
</div>

<h1><a class="word" href="#" onclick="touchItem('#{s}')">#{t}</a></h1>
#{s2view txt}
<div>Read More...</div>
</div>
EOD
end

def allItems()
  a = [xmain(files[0])]
  (1 .. files.size-1).each{|i| a.push xsub(files[i])}
  a.join
end

def main

  if cgip(:touch)
    s = files[0]
    return "" if s == cgip(:touch)
    FileUtils.touch("d/#{CGI.escape cgip(:touch)}")
    return contentJson(<<EOD)
{
  "main" : #{s2json xmain(cgip(:touch))},
  "sub"  : #{s2json xsub(s)}
}
EOD
  end

  if cgip(:open)
  end
  if cgip(:close)
  end
  if cgip(:html)
  end
  if cgip(:text)
  end
  if cgip(:write)
  end
  if cgip(:search)
  end

  return <<EOD
Content-type: text/html; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Script-Type" content="text/javascript" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="robots" content="noindex,nofollow">
  <meta name="robots" content="noarchive">
  <meta name="viewport" content="width=device-width">
  <title> #{SITE_NAME} </title>
  <link rel="shortcut icon" href="favicon.ico" /> 
  <script type="text/javascript" src="./jquery-2.1.3.min.js"></script>
  <script type="text/javascript" src="./shortcut.js"></script>
  <script type="text/javascript" src="./masonry.pkgd.min.js"></script>
</head>
<style type="text/css">#{CSS}</style>
<script type="text/javascript">#{SCRIPT}</script>
<body>
<!-- ================================== -->
<div id="header">
Word <input id="word" type="text" size="12" name="word" value=""/>
<div style="float:right">
#{SITE_NAME}
</div>
</div>
<!-- ================================== -->
<div class="masonry">
<!-- ================================ -->
#{allItems()}
<!-- ================================ -->
</div>
<!-- ================================== -->
</body>
</html>
EOD
end

puts main
