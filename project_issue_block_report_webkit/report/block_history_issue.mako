## -*- coding: utf-8 -*-
<html>
<head>
       <style type="text/css">
          ${css}
	    </style>

   </head>
<body>
    <h4 style="clear:both;">${_(u'Issues Report')}</h4>
    %for issue in get_related_issue(objects) :
    <% setLang(issue.partner_id.lang) %>
    <table width="1080px" class="list_main_table" style="background-color: #EEEEEE;">
        <th>${_("Issue:")}&nbsp;[${ issue.id | entity }]&nbsp;${ issue.name | entity }</th>
    </table>
    <br />
	    <table width="100%" class="list_main_table">
        <tr>
            <th>${_("Date")}</th>
            <th>${_("Subject")}</th>
            <th>${_("Description")}</th>
        </tr>
	        %for message in get_issue_message(issue) :
	        <tr>
	            <td style='white-space: nowrap;'>${ formatLang(message['date'], date=True) }</td>
	            <td style='white-space: nowrap;'>${ message['subject'] }</td>
	            <td>${ message['body'] | n }</td>
	        </tr>
	        %endfor
	    </table>
    <p style="page-break-after:always"/>
    %endfor
</body>
</html>
