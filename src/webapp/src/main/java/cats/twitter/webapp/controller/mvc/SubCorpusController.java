package cats.twitter.webapp.controller.mvc;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import javax.servlet.http.HttpServletResponse;
import javax.transaction.Transactional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.SessionAttributes;
import org.springframework.web.servlet.ModelAndView;

import cats.twitter.exceptions.NotFoundException;
import cats.twitter.model.Corpus;
import cats.twitter.model.SubCorpus;
import cats.twitter.model.User;
import cats.twitter.repository.CorpusRepository;
import cats.twitter.webapp.service.SubCorpusService;

@Controller
@RequestMapping("/sub")
@SessionAttributes({ "twitter", "user" })
public class SubCorpusController
{
	private final Logger log = LoggerFactory.getLogger(SubCorpusController.class);

	/**
	 * @param principal
	 *            Current authenticated user
	 * @return the form of creation of a corpus
	 */
	@Autowired
	CorpusRepository corpusRepository;
	@Autowired
	SubCorpusService service;

	@RequestMapping(method = RequestMethod.GET)
	public ModelAndView initForm(@ModelAttribute("user") User principal)
	{
		ModelAndView mv = new ModelAndView("createSub");
		List<Corpus> corpuses = corpusRepository.findByUser(principal);
		mv.addObject("corpuses",corpuses);
		return mv;
	}

	@RequestMapping(value = "/{id}", method = RequestMethod.GET)
	public ModelAndView pageAll(@PathVariable("id") Long id, @ModelAttribute User user)
	{
		ModelAndView model = new ModelAndView("subDetails");
		SubCorpus sub = service.getSubCorpus(id);
		model.addObject("sub",sub);
		return model;
	}

	@Transactional
	@RequestMapping(method = RequestMethod.POST)
	public String createSubCorpus(
		@RequestParam("corpusId") long corpusId,
		@RequestParam(value = "name", required = false) String name,
		@RequestParam(value = "regexp", required = false) String regexp,
		@RequestParam(value = "hashtags", required = false) String hashtags,
		@RequestParam(value = "mentions", required = false) String mentions,
		@ModelAttribute("user") User user,
		Model model)
	{
		Optional<String> regexpOp = regexp == null ? Optional.empty() : Optional.of(regexp);
		String[] tags = hashtags.replace(" ","").split(",");
		String[] ments = mentions.replace(" ","").split(",");
		Optional<String[]> hashtagsOp = tags == null ? Optional.empty() : Optional.of(tags);
		Optional<String[]> mentionsOp = ments == null ? Optional.empty() : Optional.of(ments);

		SubCorpus sub = service.createSubCorpus(corpusId,name,regexpOp,hashtagsOp,mentionsOp);

		return "redirect:/sub/" + sub.getId();
	}

	@RequestMapping(value = "/{idRoute}/sub.csv")
	public void toCSV(@PathVariable("idRoute") long id,
		HttpServletResponse response,
		@ModelAttribute User user) throws IOException
	{
		String csvFileName = "exportSubCorpus" + id + ".csv";

		response.setContentType("text/csv");

		// creates mock data
		String headerKey = "Content-Disposition";
		String headerValue = String.format("attachment; filename=\"%s\"",
			csvFileName);
		response.setHeader(headerKey,headerValue);

		service.exportCSV(user,id,response.getWriter());
	}

	/**
	 * @param authentication
	 * @return
	 */
	@ModelAttribute("user")
	public User getUserFromAuth(Authentication authentication)
	{
		return (User) authentication.getPrincipal();
	}

	@ExceptionHandler(NotFoundException.class)
	public ModelAndView handleCorpusNotFound(NotFoundException ex)
	{
		ModelAndView modelAndView = new ModelAndView("error");
		return modelAndView;
	}
}
