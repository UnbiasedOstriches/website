
var albumBucketName = 'ostriches-in';
var bucketRegion = 'eu-central-1';
var IdentityPoolId = 'eu-central-1:9188fe2a-1b30-420e-a571-8e4adcfd7a1c';

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  params: {Bucket: albumBucketName}
});


function addFile() {
  var files = document.getElementById('fileupload').files;
  if (!files.length) {
    return alert('Please choose a file to upload first.');
  }
  var file = files[0];
  var fileName = file.name;
  var fileKey = fileName;
  s3.upload({
    Key: fileKey,
    Body: file
  }, function(err, data) {
    if (err) {
      return alert('There was an error uploading your file: ', err.message);
    }
    alert('Successfully uploaded file.');
  });
}
