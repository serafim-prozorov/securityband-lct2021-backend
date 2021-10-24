using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.StaticFiles;


namespace SecurityBand.Lct.Api
{
    [ApiController]
    [Route("api/[controller]")]
    public class JobController : ControllerBase
    {
        private static readonly ConcurrentDictionary
            <Guid, (string SourceName, string SourceExt, string ResultExt, Process Process)> Jobs = new();
        private static readonly Dictionary<string, string> FormatMap = new() {[".pdf"] = ".jpg"};


        [HttpPost]
        public async Task<IActionResult> Post(IFormFile file, CancellationToken cancellationToken)
        {
            var jobId = Guid.NewGuid();
            var srcName = Path.GetFileNameWithoutExtension(file.FileName);
            var srcExt = Path.GetExtension(file.FileName);
            var resultExt = FormatMap.TryGetValue(srcExt, out var mappedExt) ? mappedExt : srcExt;
            
            await using var stream = System.IO.File.Create($"{jobId}{srcExt}");
            await file.CopyToAsync(stream, cancellationToken);

           var process = Process.Start($"python", $"./ML/main.py ../{jobId}{srcExt}");
            
            if (process is null)
            {
                return StatusCode(500, "Unable to start cleanup job");
            }

            Jobs[jobId] = (srcName, srcExt, resultExt, process);

            return Created($"/api/job/{jobId}", new {id = jobId});
        }

        [HttpGet("{id:guid}")]
        public IActionResult Get([FromRoute] Guid id)
        {
            if (!Jobs.TryGetValue(id, out var job))
                return NotFound();

            var resultFileName = $"{id}_processed{job.ResultExt}";
            
            if (!job.Process.HasExited)
                 return Accepted();

            if (!System.IO.File.Exists(resultFileName))
                return UnprocessableEntity();
            
            var srcFileName = $"{id}.{job.SourceExt}";
            if (System.IO.File.Exists(srcFileName))
            {
                System.IO.File.Delete(srcFileName);
            }

            return Ok(resultFileName);
        }
        
        [HttpGet("{id}/result")]
        [ProducesResponseType(typeof(FileResult), 200)]
        public IActionResult GetFile([FromRoute] Guid id, [FromServices] IContentTypeProvider contentTypeProvider)
        {
            if (!Jobs.TryGetValue(id, out var job))
                return NotFound();

            var resultFileName = $"{id}_processed{job.ResultExt}";

            if (!job.Process.HasExited)
                return Forbid();

            if (!System.IO.File.Exists(resultFileName))
                return UnprocessableEntity();
            
            var contentType = contentTypeProvider.TryGetContentType(job.ResultExt, out var tmpContentType)
                ? tmpContentType
                : "application/octet-stream";

            return File(
                System.IO.File.OpenRead(resultFileName),
                contentType,
                $"{id}__{job.SourceName}{job.ResultExt}");
        }
    }
}