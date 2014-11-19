## -*- coding: utf-8 -*-
<html>
<head>
       <style type="text/css">
          ${css}
	    </style>

   </head>
<body>
    <h4 style="clear:both;">${_(u'Issues Report')}</h4>
    %for project in get_related_projects(objects) :
    <% setLang(project.partner_id.lang) %>
    <table width="100%" class="list_main_table" style="background-color: #EEEEEE;">
        <th>${_("Project:")}&nbsp;${ project.name | entity }</th>
    </table>
    <br />
     
 
        %for issue_type in get_related_issue(project) :
        %if issue_type['issues']:
	    <table width="100%" class="list_main_table" style="background-color: ${issue_type['color']};">
	        <th>${_("Issue State:")}&nbsp;${ issue_type['type'].name | entity }</th>
	    </table>
	    <table width="100%" class="list_main_table">
        <tr>
            <th>${_("Ref")}</th>
            <th>${_("Date")}</th>
            <th>${_("Description")}</th>
        </tr>
	        %for issue in issue_type['issues'] :
	        <tr>
	            <td>${ _('REF')+str(issue.id) | entity }</td>
	            <td style='white-space: nowrap;'>${ formatLang(issue.create_date, date=True) }</td>
	            <td>${ issue.name | entity }</td>
	        </tr>
	        %endfor
	    </table>
	    %endif
        %endfor
    <p style="page-break-after:always"/>
    %endfor
</body>
</html>
