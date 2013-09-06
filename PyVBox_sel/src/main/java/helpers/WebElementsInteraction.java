package helpers;

import org.jbehave.web.selenium.*;
import org.jbehave.web.selenium.WebDriverProvider;
import org.jbehave.web.selenium.WebDriverPage;
import org.openqa.selenium.*;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.By;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.WebElement;
import org.testng.annotations.AfterClass;
import org.testng.annotations.Test;
import org.testng.annotations.*;

import java.util.ArrayList;
import java.util.List;
import java.lang.String;
import java.lang.Object;

/**
 * Created with IntelliJ IDEA.
 * User: sneha
 * Date: 01/11/2012
 * Time: 14:51
 * To change this template use File | Settings | File Templates.
 */
public class WebElementsInteraction {

    private WebDriver driver;
    private WebElement ele;


    private boolean highlight = Boolean.parseBoolean(System.getProperty("driver.highlight","true"));


    public void clickElement(WebDriver driver, By by)
    {
        this.driver = driver;
          ele = waitUntilVisible(driver, by);
          ele = this.driver.findElement(by);
          ele.click();
    }

    public void inputKeys(WebDriver driver, String inputFieldName, String inputValue )
    {
        this.driver = driver;
        ele = waitUntilVisible(driver, By.name(inputFieldName));
        ele = this.driver.findElement(By.name(inputFieldName));
        ele.sendKeys(inputValue);
        ele.submit();
    }

    /**
     * Wait until all checkboxes are visible on the page - poll until no more appaear
     * We need to do this in order to prevent StaleElementReferenceExceptions
     * @param by
     */
    public void waitForCheckboxes(WebDriver driver, By by) {
        pause(5);
        List<WebElement> checkboxes = waitUntilElementsVisible(driver,by);
        int numCheckboxesBefore = -1;
        int numCheckboxesNow = checkboxes.size();
        while (numCheckboxesNow > numCheckboxesBefore) {
            // We must wait here otherwise the page may still be loading but may not have changed compared to the last time we checked
            pause(5);
            checkboxes = waitUntilElementsVisible(driver, by);
            numCheckboxesBefore = numCheckboxesNow;
            numCheckboxesNow = checkboxes.size();
        }
    }

    public void pause(long seconds) {
        try {
            synchronized (this) {
                this.wait(seconds * 1000);
            }
        } catch (Exception e) {
            System.out.println("Failed to wait for " + seconds + " seconds: " + e.getMessage());
            // Wait again until we exceed the wait period
        }
    }

    /**
     * Select a single checkbox by it's text value. It will not select a checkbox if it has already been selected.
     *
     * <p>
     * The selector must refer to <strong> the checkbox element with the accompanying text. </strong>
     * </p>
     *
     * <p>
     * e.g. the HTML:
     *
     * <pre>
     * {@code <label class="selectit">
     *    <input id="in-popular-topic-1295" type="checkbox" value="1295"/>
     *    Export Process
     * </label> }
     * </pre>
     *
     * <p>
     * The xpath here should be <code> //*[@class='selectit'] </code> and <strong> NOT </strong>
     * <code> //*[@class='selectit']/input </code>
     *
     * @param by
     *          The selector of the entire checkbox element with accompanying text
     * @param checkboxText
     *          The text of the element you want to de-select
     */
    public void selectCheckBoxByText(WebDriver driver, By by, String checkboxText)
    {
        highlight = false; //force highlighting off for performance
        List<WebElement> checkboxes = driver.findElements(by);
        waitUntilVisible(driver,by);
        for(WebElement checkbox : checkboxes)
        {
            System.out.println("CHECKING CHECKBOX !!!!!" + checkbox.getText());
            //if the checkbox text matches and it isn't selected in the UI already
            if(checkbox.getText().equals(checkboxText) && !checkbox.isSelected() && checkbox.isDisplayed())
            {
                checkbox.click();
                //checkbox found
                break;
            }
        }
        highlight = Boolean.parseBoolean(System.getProperty("driver.highlight", "true"));
    }

    /**
     * De-selects a single checkbox by it's text value. It will not de-select a checkbox if it has already been de-selected.
     *
     * <p>
     * The selector must refer to <strong> the checkbox element with the accompanying text. </strong>
     * </p>
     *
     * <p>
     * e.g. the HTML:
     *
     * <pre>
     * {@code <label class="selectit">
     *    <input id="in-popular-topic-1295" type="checkbox" value="1295"/>
     *    Export Process
     * </label> }
     * </pre>
     *
     * <p>
     * The xpath here should be <code> //*[@class='selectit'] </code> and <strong> NOT </strong>
     * <code> //*[@class='selectit']/input </code>
     *
     * @param by
     *          The selector of the entire checkbox element with accompanying text
     * @param checkboxText
     *          The text of the element you want to de-select
     */
    public void deselectCheckboxByText(WebDriver driver, By by, String checkboxText) {
        highlight = false; // force highlighting off for performance
        List<WebElement> checkboxes = driver.findElements(by);

        for (WebElement checkbox : checkboxes) {
            // if the checkbox text matches and it is selected in the UI already
            if (checkbox.getText().equals(checkboxText) && checkbox.isSelected() && checkbox.isDisplayed()) {
                checkbox.click();
                break; // Checkbox found
            }
        }
        highlight = Boolean.parseBoolean(System.getProperty("driver.highlight", "true"));
    }

    /**
     * De-select all checkboxes on a page.
     *
     * <p>
     * The selector must refer to <strong> the checkbox element only without the accompanying text. </strong>
     * </p>
     *
     * <p>
     * e.g. the HTML:
     *
     * <pre>
     * {@code <label class="selectit">
     *    <input id="in-popular-topic-1295" type="checkbox" value="1295"/>
     *    Export Process
     * </label> }
     * </pre>
     *
     * <p>
     * The xpath here should be <code> //*[@class='selectit']/input </code> and <strong> NOT </strong>
     * <code> //*[@class='selectit'] </code>
     *
     *
     * @param by
     */
    public void deselectAllCheckboxes(WebDriver driver,By by) {
        highlight = false; // force highlighting off for performance
        List<WebElement> checkboxes = driver.findElements(by);

        for (WebElement checkbox : checkboxes) {
            if (checkbox.isSelected() && checkbox.isDisplayed()) {
                checkbox.click();
            }
        }
        highlight = Boolean.parseBoolean(System.getProperty("driver.highlight", "true"));
    }

    /**
     * Select many checkboxes by their text value. It will not select a checkbox if it has already been selected.
     *
     * You can still use this to select a single checkbox too.
     *
     * <p>
     * The selector must refer to <strong> the checkbox element with the accompanying text. </strong>
     * </p>
     *
     * <p>
     * e.g. the HTML:
     *
     * <pre>
     * {@code <label class="selectit">
     *    <input id="in-popular-topic-1295" type="checkbox" value="1295"/>
     *    Export Process
     * </label> }
     * </pre>
     *
     * <p>
     * The xpath here should be <code> //*[@class='selectit'] </code> and <strong> NOT </strong>
     * <code> //*[@class='selectit']/input </code>
     *
     * @param by
     *          The selector of <strong> ALL </strong> the checkboxes on the page
     * @param checkboxesTextToSelect
     *          The text of the checkboxes you want to select
     * @return the number of checkboxes selected
     */
    public int selectCheckboxesByText(By by, String[] checkboxesTextToSelect) {
        highlight = false; // force highlighting off for performance
        List<String> checkboxesText = new ArrayList<String>(checkboxesTextToSelect.length);

        for (String text : checkboxesTextToSelect) {
            checkboxesText.add(text.trim());
        }

        // Trim the whitespace as we are adding the elements into the ArrayList
        for (String text : checkboxesTextToSelect) {
            checkboxesText.add(text.trim());
        }

        // Wait until all the checkboxes are visible to prevent StaleElementReferenceExceptions
        List<WebElement> checkboxes = waitUntilElementsVisible(driver,by);
        int numCheckboxesBefore = -1;
        int numCheckboxesNow = checkboxes.size();
        while (numCheckboxesNow > numCheckboxesBefore) {
            checkboxes = waitUntilElementsVisible(driver,by);
            numCheckboxesBefore = numCheckboxesNow;
            numCheckboxesNow = checkboxes.size();
        }

        int i = 0;
        for (WebElement checkbox : checkboxes) {
            // if it isn't selected already
            if (checkboxesText.contains(checkbox.getText()) && !checkbox.isSelected() && checkbox.isDisplayed()) {
                checkboxesText.remove(checkbox.getText());
                checkbox.click();
                i++;

                // if it is already selected
            } else if (checkboxesText.contains(checkbox.getText()) && checkbox.isSelected() && checkbox.isDisplayed()) {
                checkboxesText.remove(checkbox.getText()); // remove the found checkbox from our list
            }

            // Break out of the loop if we have found all our applicable checkboxes (or they were clicked already)
            if (checkboxesText.isEmpty()) {
                break;
            }
        }
        highlight = Boolean.parseBoolean(System.getProperty("driver.highlight", "true"));
        return i;
    }


    public void hoverAndVerifyLink(WebDriver driver, By byParent, By byChild) {
        WebElement menu = waitUntilClickable(driver, byParent);

        // Use the Advanced User Interactions API to perform a hover
        Actions builder = new Actions(driver);
        builder.moveToElement(menu).perform(); // hover

        waitUntilClickable(driver, byChild);
    }

    public void hoverAndVerifyLinks(WebDriver driver, By byParent, ArrayList<By> byChildren) {
        waitUntilClickable(driver, byParent);

        // Use the Advanced User Interactions API to perform a hover
        Actions builder = new Actions(driver);
        builder.moveToElement(driver.findElement(byParent)).perform(); // hover

        for (By child : byChildren) {
            waitUntilClickable(driver, child);
        }
    }

    /**
     * Click a hidden menu item, exposed by hovering over the menu (AKA hover and click).
     *
     * @param byMenu
     *          The selector of the main menu parent item.
     * @param byMenuItem
     *          The selector of the hidden/drop-down menu item.
     */
    public void hoverAndClick(WebDriver driver, By byMenu, By byMenuItem) {
        WebElement menu = waitUntilClickable(driver, byMenu);
        WebElement menuOption = driver.findElement(byMenuItem); // this will be invisible in the UI so find in the page HTML

        // Use the Advanced User Interactions API to perform a hover and click
        Actions builder = new Actions(driver);
        builder.moveToElement(menu).perform(); // hover

        waitUntilClickable(driver, byMenuItem);
        menuOption.click();
    }

    /**
     * Hovers over an element in the dom.
     *
     * @param by
     *          Seletor to use for finding the item to hover over
     */
    public void hover(WebDriver driver, By by) {
        WebElement element = waitUntilClickable(driver, by);

        Actions builder = new Actions(driver);
        builder.moveToElement(element);
    }

    /*
    /**
     * A regular click does not always work.
     * In that case use this function instead
     * @param by

    public void safeClick(WebDriver driver, By by){
        WebElement element = waitUntilClickable(by);
        Actions builder = new Actions(this.getDriverProvider().get());
        builder.moveToElement(element).click().build().perform();
    }  */

    /*public void clickRadioButton(WebDriver driver, String Xpath)
    {
        this.driver=driver;
        ele=driver.findElement(By.xpath(Xpath));
        ele.click();
    }   */

    /**
     * Verify that the expected text is contained within the given element's text.
     *
     * @param by
     *          The selector of the element.
     * @param expectedText
     *          The expected text that the element should have.
     */
    public boolean elementContainsText(WebDriver driver, By by, String expectedText)
    {
        String elementText = waitUntilVisible(driver, by).getText();

        if(!elementText.contains(expectedText.trim()))
        {
            throw new NoSuchElementException("The found text (" + elementText + ") does not match the expected text (" + expectedText + ")." + "\n The current URL is: " + driver.getCurrentUrl());
        }
        return true;
    }

    /**
     * Wait for a specific element to appear on the page.
     *
     * @param by
     *          The selector of the element.
     */
    public boolean waitForElement(WebDriver driver, By by) {
        waitUntilVisible(driver, by);
        return true;
    }

    /**
     * Wait for a specific element to disappear off the page or to check it isn't there.
     *
     * @param by
     *          The selector of the element.
     * @return true if the element is NOT present.
     */
    public boolean waitForElementToDisappear(WebDriver driver, By by) {
        return waitUntilInvisible(driver, by);
    }


    /*--------------------------Private methods ----------------------------

     */

    /**
     * Wait for an element to be visible AND clickable in the UI.
     *
     * @param by
     * @return
     */
    private WebElement waitUntilVisible(WebDriver driver, By by)
    {
        WebElement element = null;
        try
        {
            element = new WebDriverWait(driver,20,1000).until(ExpectedConditions.visibilityOfElementLocated(by));
            if(highlight)
            {
                highlightElement(driver, element);
            }
        }
        catch(TimeoutException e)
        {
            throw new NoSuchElementException("***FAILED to find the element specified by:" + by + " on page: " + driver.getCurrentUrl() + ".Check your selector !!**" + e.toString());
        }

        return element;

    }



    private List<WebElement> waitUntilElementsVisible(WebDriver driver, By by) {
        List<WebElement> elements = new WebDriverWait(driver, 120, 1000).until(ExpectedConditions.presenceOfAllElementsLocatedBy(by));

       if(highlight)
       {
           for(WebElement element: elements)
           {
               highlightElement(driver, element);
           }
       }
        // no exception thrown if nothing is found so we must do it ourselves
        if (elements.isEmpty()) {
            throw new NoSuchElementException("***FAILED to find the elements specified by: " + by + " on page: " + driver.getCurrentUrl()
                    + ". Check your selector!!***");
        }
        return elements;
    }


    /**
     * Wait for an element to be visible AND clickable in the UI.
     *
     * @param by
     * @return
     */
    private WebElement waitUntilClickable(WebDriver driver, final By by) {
        WebElement element;

        try {
            element = new WebDriverWait(driver, 120, 1000).until(ExpectedConditions.elementToBeClickable((by)));
        } catch (TimeoutException e) {
            throw new NoSuchElementException("***FAILED to find the element specified by: " + by + " on page: " + driver.getCurrentUrl()
                    + ". Check your selector!!***");
        }
        return element;
    }

    /**
     * Wait for an element to be invisible in the UI.
     *
     * @param by
     * @return
     */
    private boolean waitUntilInvisible(WebDriver driver, By by) {

        try {
           WebElement element = new WebDriverWait(driver, 120, 1000).until(ExpectedConditions.visibilityOfElementLocated(by));

            if(highlight)
            {
                highlightElement(driver, element);
            }

        } catch (TimeoutException e) {
            return true;
        }

        throw new WebDriverException("**FAILED waiting for the element specified by: " + by + " to disappear/not be on the page.**");
    }

    /**
     * Set an attribute in the UI.
     *
     * <p>
     * <b> **DANGEROUS** </b> IF YOU DON'T KNOW WHAT YOU'RE DOING.
     *
     * @param element
     *          a WebElement
     * @param attributeName
     *          the attribute
     * @param value
     *          a value to give the attribute
     */
    private void setAttribute(WebDriver driver, WebElement element, String attributeName, String value) {
        JavascriptExecutor js = (JavascriptExecutor) driver;
        js.executeScript("arguments[0].setAttribute(arguments[1], arguments[2])", element, attributeName, value);
    }

    /**
     * Highlight an element in the UI.
     *
     * @param element
     *          a WebElement
     */
    protected void highlightElement(WebDriver driver, WebElement element) {
        final int wait = 50;
        String original = element.getAttribute("style");
        try {
            setAttribute(driver, element, "style", "color: yellow; border: 5px solid yellow; background-color: black;");
            Thread.sleep(wait);
            setAttribute(driver, element, "style", "color: black; border: 5px solid black; background-color: yellow;");
            Thread.sleep(wait);
            setAttribute(driver, element, "style", "color: yellow; border: 5px solid yellow; background-color: black;");
            Thread.sleep(wait);
            setAttribute(driver, element, "style", "color: black; border: 5px solid black; background-color: yellow;");
            Thread.sleep(wait);
        } catch (StaleElementReferenceException e) {
        } catch (InterruptedException e2) {
        } // swallow exceptions as highlighting is not Test-critical
        setAttribute(driver, element, "style", original);
    }
}
