const escapeHtml = require('escape-html');

/**
 * Responds to an HTTP request using data from the request body parsed according
 * to the "content-type" header.
 *
 * @param {Object} req Cloud Function request context.
 * @param {Object} res Cloud Function response context.
 */
exports.convert_video = (req, res) => {
  //Get video id and desired format
  const video_id = req.query.video_id;
  const desired_format = req.query.desired_format;


  //Download raw video from raw bucket
  //Imports the Google Cloud client library
  const {Storage} = require('@google-cloud/storage');

  // Creates a client
  const storage = new Storage();

  const srcbucketName = 'cs378_final_raw_videos';
  const destbucketName = 'cs378_final_converted_videos';
  const srcFilename = video_id + '.mp4';
  const destFilename = '/tmp/' + srcFilename;

  const options = {
    // The path to which the file should be downloaded, e.g. "./file.txt"
    destination: destFilename,
  };
  /*
  // Downloads the file
  await storage
    .bucket(srcbucketName)
    .file(srcFilename)
    .download(options);
  */
  var info = "video_id: " + video_id + ",desired_format: " + desired_format; 

  res.status(200).send(info);
};
