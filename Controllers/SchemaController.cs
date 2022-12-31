using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;
using System;
using System.IO;
using System.Text;

namespace Scada.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SchemaController : ControllerBase
    {
        private readonly AppDbContext _context;

        public SchemaController(AppDbContext context)
        {
            _context = context;
        }

        // GET: api/Schema
        [HttpGet]
        public ActionResult<JObject> GetSchema()
        {
            string schema = System.IO.File.ReadAllText("schema.json");
            var result = JObject.Parse(schema);
            return Ok(result);
        }
    }
}
