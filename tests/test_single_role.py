"""Unit tests for gimme_aws_creds"""
import sys
import unittest
from contextlib import contextmanager
from io import StringIO

import requests
import responses
from nose.tools import assert_equals

import gimme_aws_creds.common as commondef
from gimme_aws_creds.aws import AwsResolver


class TestSingleRole(unittest.TestCase):
    """Class to test AWS logic in single-role case.
       Mock is used to mock external calls"""

    @contextmanager
    def captured_output(self):
        """Capture StdErr and StdOut"""
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def setUp(self):
        """Set up for the unit tests"""
        self.resolver = self.setUp_client(False)

        self.aws_signinpage = """
<!DOCTYPE HTML>
<html>
<head>
  <style type="text/css">

#loadingImage {
    margin: 10em auto;
    width: 234px;
    height: 238px;
    background-repeat: no-repeat;
    background-image: url(data:image/png;base64,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);

    -webkit-animation:spin 4s linear infinite;
    -moz-animation:spin 4s linear infinite;
    animation:spin 4s linear infinite;
}


@-moz-keyframes spin { 100% { -moz-transform: rotate(360deg); } }
@-webkit-keyframes spin { 100% { -webkit-transform: rotate(360deg); } }
@keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); } }

  </style>
</head>

<body>

  <div id="loadingImage"></div>

<script type="text/javascript">



var RegionFinder = (function()
{
    function RegionFinder( location ) {
        this.location = location;
    }

    
    RegionFinder.prototype = {

        
        getURLWithRegion: function() {
            
            var isDynamicDefaultRegion = ifPathContains(this.location.pathname, "region/dynamic-default-region");

            var queryArgs = removeURLParameter(this.location.search, "region");

            var hashArgs = this.location.href.split("#")[1] || "";
            if (hashArgs) {
                hashArgs = "#" + hashArgs;
            }

            var region = this._getCurrentRegion();
            var newArgs = "region=" + region;
            if (_shouldAuth()) {
                newArgs = "needs_auth=true";
                region = "nil";
            }

            if (queryArgs &&
                queryArgs != "?") {
                queryArgs += "&" + newArgs;
            } else {
                queryArgs = "?" + newArgs;
            }

            

            if (!region) {
                
                var contactUs = "https://portal.aws.amazon.com/gp/aws/html-forms-controller/contactus/aws-report-issue1";

                alert("How embarrassing! There is something wrong with this URL, please contact AWS at " + contactUs);
            }

            var pathname = isDynamicDefaultRegion ?  "/console/home" : this.location.pathname;

            return this.location.protocol + "//" + _getRedirectHostFromAttributes() +
                pathname + queryArgs + hashArgs;
        },

        
        _getCurrentRegion: function() {

            return _getRegionFromHash( this.location ) ||
                   _getRegionFromAttributes();
        }
    };

    

    function ifPathContains(url, parameter) {
        return (url.indexOf(parameter) != -1);
    }

    
    function removeURLParameter(url, parameter) {
        var urlparts= url.split('?');
        if (urlparts.length>=2) {
            var prefix= encodeURIComponent(parameter);
            var pars= urlparts[1].split(/[&;]/g);
            //reverse iteration as may be destructive
            for (var i= pars.length; i-- > 0;) {
                if (pars[i].lastIndexOf(prefix, 0) !== -1) {
                    pars.splice(i, 1);
                }
            }
            url= urlparts[0]+'?'+pars.join('&');
            return url;
        } else {
            return url;
        }
    }

    
    function _getRegionFromAttributes() {
        return "us-east-1";
    };

    function _shouldAuth() {
        return "";
    };

    function _getRedirectHostFromAttributes() {
    	return "console.aws.amazon.com";
    }

    
    function _getRegionFromHash( location ) {
        
        var hashArgs = "#" + (location.href.split("#")[1] || "");

        
        var hashRegionArg = "";

        
        var match = hashArgs.match("region=([a-zA-Z0-9-]+)");
        if (match && match.length > 1 && match[1]) {
            hashRegionArg = match[1];
        }
        return hashRegionArg;
    }

    return RegionFinder;
})();


var regionFinder = new RegionFinder( window.location );

window.location.href = regionFinder.getURLWithRegion();

</script>


</body>
</html>
"""
        self.saml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOlJlc3BvbnNlIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIiB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIERlc3RpbmF0aW9uPSJodHRwczovL3NpZ25pbi5hd3MuYW1hem9uLmNvbS9zYW1sIiBJRD0iaWQxNDI0NjkxOTY3Mzk3NTA5NDE1MjI0ODAxODciIElzc3VlSW5zdGFudD0iMjAyMC0xMS0yMFQxOTo1Nzo1Ny41MzlaIiBWZXJzaW9uPSIyLjAiPjxzYW1sMjpJc3N1ZXIgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIEZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOm5hbWVpZC1mb3JtYXQ6ZW50aXR5Ij5odHRwOi8vd3d3Lm9rdGEuY29tL2V4a24ydGY2eDFaeTVkWElMMHg3PC9zYW1sMjpJc3N1ZXI+PGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PGRzOlNpZ25lZEluZm8+PGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxkc2lnLW1vcmUjcnNhLXNoYTI1NiIvPjxkczpSZWZlcmVuY2UgVVJJPSIjaWQxNDI0NjkxOTY3Mzk3NTA5NDE1MjI0ODAxODciPjxkczpUcmFuc2Zvcm1zPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjZW52ZWxvcGVkLXNpZ25hdHVyZSIvPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiPjxlYzpJbmNsdXNpdmVOYW1lc3BhY2VzIHhtbG5zOmVjPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiIFByZWZpeExpc3Q9InhzIi8+PC9kczpUcmFuc2Zvcm0+PC9kczpUcmFuc2Zvcm1zPjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGVuYyNzaGEyNTYiLz48ZHM6RGlnZXN0VmFsdWU+YmxhaDwvZHM6RGlnZXN0VmFsdWU+PC9kczpSZWZlcmVuY2U+PC9kczpTaWduZWRJbmZvPjxkczpTaWduYXR1cmVWYWx1ZT5ibGFoPC9kczpTaWduYXR1cmVWYWx1ZT48ZHM6S2V5SW5mbz48ZHM6WDUwOURhdGE+PGRzOlg1MDlDZXJ0aWZpY2F0ZT5ibGFoPC9kczpYNTA5Q2VydGlmaWNhdGU+PC9kczpYNTA5RGF0YT48L2RzOktleUluZm8+PC9kczpTaWduYXR1cmU+PHNhbWwycDpTdGF0dXMgeG1sbnM6c2FtbDJwPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6cHJvdG9jb2wiPjxzYW1sMnA6U3RhdHVzQ29kZSBWYWx1ZT0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnN0YXR1czpTdWNjZXNzIi8+PC9zYW1sMnA6U3RhdHVzPjxzYW1sMjpBc3NlcnRpb24geG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSIgSUQ9ImlkMTQyNDY5MTk2NzQwNDY1MDQxMTA2ODc1OTU5IiBJc3N1ZUluc3RhbnQ9IjIwMjAtMTEtMjBUMTk6NTc6NTcuNTM5WiIgVmVyc2lvbj0iMi4wIj48c2FtbDI6SXNzdWVyIHhtbG5zOnNhbWwyPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIiBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OmVudGl0eSI+aHR0cDovL3d3dy5va3RhLmNvbS9leGtuMnRmNngxWnk1ZFhJTDB4Nzwvc2FtbDI6SXNzdWVyPjxkczpTaWduYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPjxkczpTaWduZWRJbmZvPjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIi8+PGRzOlNpZ25hdHVyZU1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZHNpZy1tb3JlI3JzYS1zaGEyNTYiLz48ZHM6UmVmZXJlbmNlIFVSST0iI2lkMTQyNDY5MTk2NzQwNDY1MDQxMTA2ODc1OTU5Ij48ZHM6VHJhbnNmb3Jtcz48ZHM6VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz48ZHM6VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIj48ZWM6SW5jbHVzaXZlTmFtZXNwYWNlcyB4bWxuczplYz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIiBQcmVmaXhMaXN0PSJ4cyIvPjwvZHM6VHJhbnNmb3JtPjwvZHM6VHJhbnNmb3Jtcz48ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxlbmMjc2hhMjU2Ii8+PGRzOkRpZ2VzdFZhbHVlPjNoNDNEQWhWNEZXd1N4RTRwcDJjRUlHNzRTVkpmdkQwVUtjQ0tDYlM1NjA9PC9kczpEaWdlc3RWYWx1ZT48L2RzOlJlZmVyZW5jZT48L2RzOlNpZ25lZEluZm8+PGRzOlNpZ25hdHVyZVZhbHVlPmJsYWg8L2RzOlNpZ25hdHVyZVZhbHVlPjxkczpLZXlJbmZvPjxkczpYNTA5RGF0YT48ZHM6WDUwOUNlcnRpZmljYXRlPmJsYWg8L2RzOlg1MDlDZXJ0aWZpY2F0ZT48L2RzOlg1MDlEYXRhPjwvZHM6S2V5SW5mbz48L2RzOlNpZ25hdHVyZT48c2FtbDI6U3ViamVjdCB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI+PHNhbWwyOk5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OnVuc3BlY2lmaWVkIj5maXJzdC5sYXN0QG5vd2hlcmUuY29tPC9zYW1sMjpOYW1lSUQ+PHNhbWwyOlN1YmplY3RDb25maXJtYXRpb24gTWV0aG9kPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6Y206YmVhcmVyIj48c2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbkRhdGEgTm90T25PckFmdGVyPSIyMDIwLTExLTIwVDIwOjAyOjU3LjU0MFoiIFJlY2lwaWVudD0iaHR0cHM6Ly9zaWduaW4uYXdzLmFtYXpvbi5jb20vc2FtbCIvPjwvc2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbj48L3NhbWwyOlN1YmplY3Q+PHNhbWwyOkNvbmRpdGlvbnMgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIE5vdEJlZm9yZT0iMjAyMC0xMS0yMFQxOTo1Mjo1Ny41NDBaIiBOb3RPbk9yQWZ0ZXI9IjIwMjAtMTEtMjBUMjA6MDI6NTcuNTQwWiI+PHNhbWwyOkF1ZGllbmNlUmVzdHJpY3Rpb24+PHNhbWwyOkF1ZGllbmNlPnVybjphbWF6b246d2Vic2VydmljZXM8L3NhbWwyOkF1ZGllbmNlPjwvc2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48L3NhbWwyOkNvbmRpdGlvbnM+PHNhbWwyOkF1dGhuU3RhdGVtZW50IHhtbG5zOnNhbWwyPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIiBBdXRobkluc3RhbnQ9IjIwMjAtMTEtMjBUMTk6NTc6NTcuNTM5WiIgU2Vzc2lvbkluZGV4PSJpZDE2MDU5MDIyNzc1MzguNTQ5Mzk0NDU1Ij48c2FtbDI6QXV0aG5Db250ZXh0PjxzYW1sMjpBdXRobkNvbnRleHRDbGFzc1JlZj51cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZFByb3RlY3RlZFRyYW5zcG9ydDwvc2FtbDI6QXV0aG5Db250ZXh0Q2xhc3NSZWY+PC9zYW1sMjpBdXRobkNvbnRleHQ+PC9zYW1sMjpBdXRoblN0YXRlbWVudD48c2FtbDI6QXR0cmlidXRlU3RhdGVtZW50IHhtbG5zOnNhbWwyPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIj48c2FtbDI6QXR0cmlidXRlIE5hbWU9Imh0dHBzOi8vYXdzLmFtYXpvbi5jb20vU0FNTC9BdHRyaWJ1dGVzL1JvbGUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5hcm46YXdzOmlhbTo6MDEyMzQ1Njc4OTAxOnNhbWwtcHJvdmlkZXIvT0tUQS1JRFAsYXJuOmF3czppYW06OjAxMjM0NTY3ODkwMTpyb2xlL3Rlc3Ryb2xlMTwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PHNhbWwyOkF0dHJpYnV0ZSBOYW1lPSJodHRwczovL2F3cy5hbWF6b24uY29tL1NBTUwvQXR0cmlidXRlcy9Sb2xlU2Vzc2lvbk5hbWUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6YmFzaWMiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPmZpcnN0Lmxhc3RAbm93aGVyZS5jb208L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0iaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS9TQU1ML0F0dHJpYnV0ZXMvU2Vzc2lvbkR1cmF0aW9uIiBOYW1lRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXR0cm5hbWUtZm9ybWF0OmJhc2ljIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj40MzIwMDwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PC9zYW1sMjpBdHRyaWJ1dGVTdGF0ZW1lbnQ+PC9zYW1sMjpBc3NlcnRpb24+PC9zYW1sMnA6UmVzcG9uc2U+Cg=="

        self.roles = []
        self.roles.append(commondef.RoleSet(idp='arn:aws:iam::012345678901:saml-provider/OKTA-IDP', 
                                            role='arn:aws:iam::012345678901:role/testrole1',
                                            friendly_account_name='SingleAccountName',
                                            friendly_role_name='testrole1'))

    def setUp_client(self, verify_ssl_certs):
        resolver = AwsResolver(verify_ssl_certs)
        resolver.req_session = requests
        return resolver

    @responses.activate
    def test_enumerate_saml_roles(self):
        """Test handling users with just one role"""
        responses.add(responses.POST, 'https://signin.aws.amazon.com/saml', status=200, body=self.aws_signinpage)
        result = self.resolver._enumerate_saml_roles(self.saml, 'https://signin.aws.amazon.com/saml')
        assert_equals(result[0], self.roles[0])
